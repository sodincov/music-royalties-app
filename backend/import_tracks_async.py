# import_tracks_async.py
import asyncio
import sys
import os
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Импортируем модели и настройки
from app.sqlmodels.track import Track
from app.sqlmodels.artist import Artist
from app.sqlmodels.album import Album
from app.sqlmodels.track_artist import TrackArtist
from app.database import AsyncSessionLocal  # ← твой AsyncSession

async def import_tracks():
    print("Чтение Excel-файла...")
    df = pd.read_excel("tracks_with_artists.xlsx", sheet_name="Sheet1")
    df = df.dropna(subset=["Название трека"])
    print(f"Найдено {len(df)} треков для импорта.")

    async with AsyncSessionLocal() as session:
        for idx, row in df.iterrows():
            try:
                title = str(row["Название трека"]).strip()
                album_title = str(row["Название альбома"]).strip()
                isrc = row.get("ISRC")
                lyrics = row.get("Автор слов") or ""
                music = row.get("Автор музыки") or ""

                # Ищем альбом
                result = await session.execute(
                    select(Album).where(Album.title == album_title)
                )
                album = result.scalar_one_or_none()
                if not album:
                    print(f"⚠️ Альбом не найден: '{album_title}' → пропускаем трек '{title}'")
                    continue

                # Собираем артистов и доли
                artists_info = []
                artist_names = []

                for i in range(1, 5):
                    art_col = f"Артист_{i}"
                    share_col = "Доля монетизации" if i == 1 else f"Доля монетизации.{i-1}"
                    artist_name = row.get(art_col)
                    share_val = row.get(share_col)

                    if pd.notna(artist_name) and artist_name.strip():
                        artist_name = artist_name.strip()
                        share_str = str(share_val).replace('%', '').strip() if pd.notna(share_val) else "0"
                        artists_info.append(f"{artist_name}:{share_str}%")
                        artist_names.append(artist_name)

                if not artist_names:
                    print(f"⚠️ Нет артистов для трека '{title}' → пропускаем")
                    continue

                # Проверяем, что все артисты существуют
                result = await session.execute(
                    select(Artist).where(Artist.name.in_(artist_names))
                )
                db_artists = result.scalars().all()
                found_names = {a.name for a in db_artists}
                missing = set(artist_names) - found_names
                if missing:
                    print(f"⚠️ Артисты не найдены: {missing} → пропускаем трек '{title}'")
                    continue

                monetization_str = ", ".join(artists_info)

                # Создаём трек
                new_track = Track(
                    title=title,
                    album_id=album.id,
                    isrc=isrc if pd.notna(isrc) else None,
                    genre=None,
                    music_authors=str(music),
                    lyrics_authors=str(lyrics),
                    artist_monetization_shares=monetization_str,
                    is_ringtone_added=False,
                    has_video_clip=False,
                    is_lyrics_added=bool(lyrics and "без слов" not in str(lyrics).lower()),
                    is_karaoke_sync_added=False,
                    text=None,
                    karaoke=None,
                    synclab=None,
                    copyright=None,
                    related_rights=None,
                    advance=None,
                    marketing=None,
                    marketing_expenses=None,
                    advance_expenses=None,
                )
                session.add(new_track)
                await session.flush()

                # Связываем с артистами
                for db_artist in db_artists:
                    ta = TrackArtist(track_id=new_track.id, artist_id=db_artist.id)
                    session.add(ta)

                await session.commit()
                print(f"✅ Добавлен трек: {title} в альбом {album_title}")

            except Exception as e:
                print(f"❌ Ошибка при обработке трека '{title}': {e}")
                await session.rollback()

    print("✅ Импорт завершён!")

if __name__ == "__main__":
    asyncio.run(import_tracks())