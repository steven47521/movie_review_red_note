import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from sqlalchemy.orm import Session

from app.clients.openai_image_client import OpenAIImageClient, OpenAIImageClientError
from app.models.creation_session import CreationSession, SessionStatus
from app.models.draft_version import DraftVersion
from app.models.image_asset import ImageAsset
from app.models.movie_meta import MovieMeta
from app.models.review_message import MessageRole, ReviewMessage, ReviewPhase

STYLES_PATH = Path(__file__).resolve().parent.parent / "seeds" / "visual_styles.json"

IMAGE_TYPE_LABELS = {
    "cover": "封面",
    "quote_card": "金句卡",
    "mood_shot": "氛围图",
    "theme_visual": "主题视觉",
}


class VisualServiceError(Exception):
    pass


class VisualService:
    def __init__(
        self,
        db: Session | None = None,
        image_client: OpenAIImageClient | None = None,
    ):
        self.db = db
        self.image_client = image_client or OpenAIImageClient()
        with STYLES_PATH.open(encoding="utf-8") as f:
            self._styles: dict = json.load(f)

    def generate_all(self, session_id: str) -> list[ImageAsset]:
        if not self.db:
            raise VisualServiceError("Database session required")

        session = self.db.get(CreationSession, session_id)
        if not session:
            raise VisualServiceError(f"Session not found: {session_id}")

        draft = self._latest_draft(session_id)
        if not draft:
            raise VisualServiceError("Draft required before image generation")

        meta = self.db.query(MovieMeta).filter_by(session_id=session_id).first()
        movie = {
            "title": meta.title if meta else session.movie_title,
            "genres": (meta.genres if meta else []) or [],
        }
        angle = session.selected_angle or {}
        style_key, style = self._pick_style(movie.get("genres") or [])
        quote = self._extract_quote(draft)

        specs = [
            ("cover", style["cover_template"].format(
                title=movie["title"], style_hint=style["label"], angle=angle.get("title", "")
            )),
            ("quote_card", style["quote_template"].format(
                quote=quote, style_hint=style["label"]
            )),
            ("mood_shot", style["mood_template"].format(
                title=movie["title"], angle=angle.get("title", ""), style_hint=style["label"]
            )),
        ]
        if len(draft.body) > 200:
            specs.append(
                ("theme_visual", style["theme_template"].format(
                    title=movie["title"], angle=angle.get("title", ""), style_hint=style["label"]
                ))
            )

        session.status = SessionStatus.IMAGE_GENERATING.value
        self.db.commit()

        generated: list[tuple[str, str, str]] = []
        with ThreadPoolExecutor(max_workers=min(4, len(specs))) as pool:
            futures = {
                pool.submit(
                    self.image_client.generate,
                    prompt=prompt,
                    image_type=image_type,
                    session_id=session_id,
                ): (image_type, prompt)
                for image_type, prompt in specs
            }
            for future in as_completed(futures):
                image_type, prompt = futures[future]
                try:
                    url = future.result()
                    generated.append((image_type, prompt, url))
                except OpenAIImageClientError as exc:
                    raise VisualServiceError(
                        f"Failed to generate {image_type}: {exc}"
                    ) from exc

        assets: list[ImageAsset] = []
        for image_type, prompt, url in sorted(generated, key=lambda item: item[0]):
            asset = self._persist_image(
                session_id=session_id,
                image_type=image_type,
                prompt=prompt,
                style_key=style_key,
                url=url,
                version=1,
                review_round=0,
            )
            assets.append(asset)

        session.status = SessionStatus.IMAGE_REVIEWING.value
        self.db.commit()
        self._record_images_in_chat(session_id, assets, event="generated")
        return assets

    def regenerate_image(self, image_id: str, reason: str = "") -> ImageAsset:
        if not self.db:
            raise VisualServiceError("Database session required")

        current = self.db.get(ImageAsset, image_id)
        if not current:
            raise VisualServiceError(f"Image not found: {image_id}")

        prompt = current.prompt
        if reason:
            prompt = f"{prompt}\nRevision note: {reason}"

        asset = self._create_image(
            session_id=current.session_id,
            image_type=current.type,
            prompt=prompt,
            style_key=current.style_key,
            version=current.version + 1,
            review_round=current.review_round,
        )
        self._record_images_in_chat(current.session_id, [asset], event="regenerated")
        return asset

    def regenerate_by_types(
        self, session_id: str, types: list[str], reason: str = ""
    ) -> list[ImageAsset]:
        results = []
        for image_type in types:
            asset = (
                self.db.query(ImageAsset)
                .filter_by(session_id=session_id, type=image_type)
                .order_by(ImageAsset.version.desc())
                .first()
            )
            if asset:
                results.append(self.regenerate_image(asset.id, reason=reason))
        return results

    def _create_image(
        self,
        *,
        session_id: str,
        image_type: str,
        prompt: str,
        style_key: str,
        version: int,
        review_round: int,
    ) -> ImageAsset:
        url = self.image_client.generate(
            prompt=prompt,
            image_type=image_type,
            session_id=session_id,
        )
        return self._persist_image(
            session_id=session_id,
            image_type=image_type,
            prompt=prompt,
            style_key=style_key,
            url=url,
            version=version,
            review_round=review_round,
        )

    def _record_images_in_chat(
        self,
        session_id: str,
        assets: list[ImageAsset],
        *,
        event: str,
    ) -> None:
        if not self.db or not assets:
            return

        session = self.db.get(CreationSession, session_id)
        round_num = max((session.image_review_round if session else 0), 1)
        labels = [IMAGE_TYPE_LABELS.get(asset.type, asset.type) for asset in assets]

        if event == "generated":
            content = f"已生成 {len(assets)} 张配图：{'、'.join(labels)}。"
            role = MessageRole.SYSTEM.value
        else:
            label = IMAGE_TYPE_LABELS.get(assets[0].type, assets[0].type)
            content = f"已重生成{label}（v{assets[0].version}）。"
            role = MessageRole.WRITER.value

        self.db.add(
            ReviewMessage(
                session_id=session_id,
                phase=ReviewPhase.IMAGE.value,
                round=round_num,
                role=role,
                content=content,
                attachment={
                    "images": [
                        {
                            "id": asset.id,
                            "type": asset.type,
                            "url": asset.url,
                            "label": IMAGE_TYPE_LABELS.get(asset.type, asset.type),
                            "version": asset.version,
                        }
                        for asset in assets
                    ]
                },
            )
        )
        self.db.commit()

    def _persist_image(
        self,
        *,
        session_id: str,
        image_type: str,
        prompt: str,
        style_key: str,
        url: str,
        version: int,
        review_round: int,
    ) -> ImageAsset:
        asset = ImageAsset(
            session_id=session_id,
            type=image_type,
            url=url,
            prompt=prompt,
            style_key=style_key,
            version=version,
            review_round=review_round,
        )
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def _latest_draft(self, session_id: str) -> DraftVersion | None:
        return (
            self.db.query(DraftVersion)
            .filter_by(session_id=session_id)
            .order_by(DraftVersion.version.desc())
            .first()
        )

    def _pick_style(self, genres: list[str]) -> tuple[str, dict]:
        for key, style in self._styles.items():
            if key == "default":
                continue
            if any(g in style.get("genres", []) for g in genres):
                return key, style
        return "default", self._styles["default"]

    @staticmethod
    def _extract_quote(draft: DraftVersion) -> str:
        if draft.hooks:
            return str(draft.hooks[0])[:80]
        sentences = re.split(r"[。！？\n]", draft.body)
        for s in sentences:
            s = s.strip()
            if len(s) >= 8:
                return s[:80]
        return draft.title[:40]
