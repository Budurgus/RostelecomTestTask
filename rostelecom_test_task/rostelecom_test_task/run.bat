@echo off
REM Активация виртуального окружения (если используется)
call poetry run python main.py



REM Деактивация виртуального окружения (опционально)
deactivate