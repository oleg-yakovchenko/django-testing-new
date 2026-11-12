"""Проверка структуры домашней работы."""

from pathlib import Path
from unittest import TestCase, main

PROJECT_ROOT = Path(__file__).resolve().parent
REQUIRED_PATHS = (
    'pytest.ini',
    'requirements.txt',
    'setup.cfg',
    'ya_news/manage.py',
    'ya_news/news/pytest_tests/__init__.py',
    'ya_news/news/pytest_tests/conftest.py',
    'ya_news/news/pytest_tests/test_content.py',
    'ya_news/news/pytest_tests/test_logic.py',
    'ya_news/news/pytest_tests/test_routes.py',
)


class TestProjectStructure(TestCase):
    def test_required_files_exist(self):
        missing_paths = tuple(
            path
            for path in REQUIRED_PATHS
            if not (PROJECT_ROOT / path).is_file()
        )

        self.assertFalse(
            missing_paths,
            f'Не найдены обязательные файлы: {missing_paths}',
        )


if __name__ == '__main__':
    main()
