import functools
from typing import List, Tuple

from duplication.models import EntityData, File
from duplication.tokenizer.buckwheat import get_identifiers_sequence_from_code, recognize_languages_dir
from duplication.tokenizer.buckwheat.tokenizer import get_data_from_file
from duplication.tokenizer.buckwheat.utils import FileData, ObjectData, transform_files_list, get_full_path


class EntitiesExtractor:
    @staticmethod
    def extract_entity_from_object_data(obj: ObjectData, file_path: str) -> EntityData:
        entity_tokens = get_identifiers_sequence_from_code(obj.content, obj.lang)
        return EntityData(obj, entity_tokens, file_path)

    @staticmethod
    def extract_entity_from_file_data(file: FileData) -> List[EntityData]:
        return [EntitiesExtractor.extract_entity_from_object_data(obj, file.path)
                for obj in file.objects]

    @staticmethod
    def extract_entities_from_files_data(files: List[FileData]) -> List[EntityData]:
        def acc(value: List[EntityData], file_data: FileData) -> List[EntityData]:
            value.extend(EntitiesExtractor.extract_entity_from_file_data(file_data))
            return value

        return functools.reduce(acc, files, [])

    @staticmethod
    def extract_data_from_files(files: List[File]) -> List[FileData]:
        return [get_data_from_file(file, lang, True, False) for file, lang in files]

    @staticmethod
    def extract_data_from_directory(directory: str, granularity: str)\
            -> Tuple[List[File], List[FileData], List[EntityData]]:
        lang2files = recognize_languages_dir(directory)
        files = transform_files_list(lang2files, granularity, None)
        files = [(get_full_path(file, directory), lang) for file, lang in files]
        files_data = EntitiesExtractor.extract_data_from_files(files)
        entities = EntitiesExtractor.extract_entities_from_files_data(files_data)
        return files, files_data, entities