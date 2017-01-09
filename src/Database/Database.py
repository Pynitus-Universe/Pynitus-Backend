"""
    Pynitus - A free and democratic music playlist
    Copyright (C) 2017  Noah Hummel

    This file is part of the Pynitus program, see <https://github.com/strangedev/Pynitus>.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from typing import List

from src.Config.ConfigLoader import ConfigLoader
from src.Data.Tagging import TagReader
from src.Data.Track.Track import Track
from src.Data.Track.TrackFactory import TrackFactory
from src.Database.IDatabaseAdapter import IDatabaseAdapter
from src.Utilities import MediaScanner


class Database(object):

    adapter = None

    @classmethod
    def setDatabaseAdapter(cls, adapter: IDatabaseAdapter.__class__):
        cls.adapter = adapter

    def __init__(self, config: ConfigLoader):
        self.config = config
        self.db = Database.adapter(self.config.get("db_path"))
        self.trackFactory = TrackFactory(self.db)

        self.refreshDB()

    def refreshDB(self) -> None:
        self.db.setAllUninitialized()
        self.db.setAllUnavailable()

        # TODO: Baustelle

        # Get all local files
        for filepath in MediaScanner.iterateAudioFiles(self.config.get("musicDirectory")):
            add_track = False
            tag_info = TagReader.readTag(filepath)

            # Check if exists in db
            if not all([x in tag_info for x in ["title", "artist", "album"]]):
                add_track = True

            if not self.db.getTrack(tag_info["title"], tag_info["artist"], tag_info["album"]):
                add_track = True

            if add_track:
                self.addTrack(
                    filepath,
                    tag_info.get("title"),
                    tag_info.get("artist"),
                    tag_info.get("album"),
                    "FileTrack",
                    **tag_info
                )

            self.db.setTrackIsAvailable(tag_info["title"], tag_info["artist"], tag_info["album"])
            self.db.setTrackIsInitialized(tag_info["title"], tag_info["artist"], tag_info["album"])

        # Check remaining uninitialized tracks
        for track in [self.trackFactory.getTrack(**td) for td in self.db.getUninitialized()]:
            if track.available():
                self.db.setTrackIsAvailable(track.title, track.artist, track.album)
            self.db.setTrackIsInitialized(track.title, track.artist, track.album)

    def addTrack(
            self,
            location: str,
            title: str=None,
            artist: str=None,
            album: str=None,
            track_type: str=None,
            **kwargs
    ) -> None:
        self.db.addTrack(location, title, artist, album, track_type, **kwargs)

    def getTracks(self) -> List[Track]:
        track_dicts = self.db.getTracks()
        return [self.trackFactory.getTrack(**track_dict) for track_dict in track_dicts]

    def getArtists(self) -> List[str]:
        return self.db.getArtists()

    def getAlbums(self) -> List[str]:
        return self.db.getAlbums()

    def getAlbumsByArtist(self, artist: str) -> List[str]:
        return self.db.getAlbumsByArtist(artist)

    def getTracksByArtist(self, artist: str) -> List[Track]:
        track_dicts = self.db.getTracksByArtist(artist)
        return [self.trackFactory.getTrack(**track_dict) for track_dict in track_dicts]

    def getTracksByAlbum(self, artist: str, album: str) -> List[Track]:
        track_dicts = self.db.getTracksByAlbum(artist, album)
        return [self.trackFactory.getTrack(**track_dict) for track_dict in track_dicts]

    def getTrack(self, title: str, artist: str, album: str) -> Track:
        return self.trackFactory.getTrack(**self.db.getTrack(title, artist, album))

    def getUnimported(self) -> List[Track]:
        track_dicts = self.db.getUnimported()
        return [self.trackFactory.getTrack(**track_dict) for track_dict in track_dicts]

    def getUnavailable(self) -> List[Track]:
        track_dicts = self.db.getUnavailable()
        return [self.trackFactory.getTrack(**track_dict) for track_dict in track_dicts]
