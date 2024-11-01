from abc import ABC, abstractmethod


class BaseConfig(ABC):
    @abstractmethod
    def client_directory(self) -> str:
        pass

    @abstractmethod
    def message_size(self) -> int:
        pass

    @abstractmethod
    def meta_file_path(self) -> str:
        pass

    @abstractmethod
    def piece_size(self) -> int:
        pass

    @abstractmethod
    def buffer_size(self) -> int:
        pass

class DefaultConfig(BaseConfig):
    def client_directory(self):
        return "box/data"
    
    def message_size(self):
        return 1024 # 1KB
    
    def meta_file_path(self):
        return "box/meta.torrent.json"
    
    def piece_size(self):
        return 1024 # 1KB
    
    def buffer_size(self) -> int:
        return 1024
