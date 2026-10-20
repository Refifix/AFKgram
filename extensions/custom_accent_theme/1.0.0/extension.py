# ==============================================================================
# Метаданные расширения (обязательный словарь для Glassify Sandbox)
# ==============================================================================
GLASSIFY_EXTENSION = {
    "id": "custom_accent_theme",
    "name": "Custom Glass Accent",
    "version": "1.0.0",
    "api": 4,  # Используем Extension API 4
}


# Глобальная переменная для хранения текущего API расширения
_API = None


def _on_setting_changed(key: str, value: Any):
    """
    Обработчик изменения настроек внутри меню расширения.
    """
    if _API is None:
        return

    if key == "material_style":
        _apply_material_style(value)


def _apply_material_style(style_key: str):
    """
    Применяет выбранный профиль материала Liquid Glass.
    """
    if style_key == "deep_glass":
        # Глубокое размытие с уплотнённой заливкой
        _API.set_material_profile({
            "intensity_scale": 1.4,
            "thickness_scale": 1.2,
            "stroke_inner_dp": 0.8,
            "stroke_outer_dp": 0.3,
            "shadow_alpha": 0.12,
            "overlay_alpha_scale": 1.1,
        })
    elif style_key == "crystal_clear":
        # Прозрачное кристаллическое стекло с тонкими гранями
        _API.set_material_profile({
            "intensity_scale": 0.6,
            "thickness_scale": 0.5,
            "stroke_inner_dp": 1.2,
            "stroke_outer_dp": 0.5,
            "shadow_alpha": 0.0,
            "overlay_alpha_scale": 0.7,
        })
    else:
        # Сброс к стандартному стилю Glassify
        _API.set_material_profile(None)


def _on_strength_changed(strength: int):
    """
    Слушатель изменения силы размытия пользователя (SeekBar от 1 до 100).
    """
    if _API is not None:
        _API.log(f"Текущая сила Liquid Glass: {strength}%")


class ThemeUpdateHook(MethodHook):
    """
    Пример хука: перехватываем обновление цветов темы Telegram.
    """
    def after_hooked_method(self, param):
        if _API is not None:
            _API.log("Тема Telegram обновлена, перерисовываем элементы расширения...")


# ==============================================================================
# Точка входа при загрузке расширения
# ==============================================================================
def on_load(api):
    global _API
    _API = api

    _API.log("Расширение Custom Glass Accent успешно загружено!")

    # 1. Регистрация собственного меню настроек в Glassify
    settings_schema = [
        {
            "type": "choice",
            "key": "material_style",
            "text": "Стиль стекла",
            "subtext": "Выберите кастомный профиль преломления и границ",
            "icon": "msg_customize",
            "default": "default",
            "options": [
                {
                    "value": "default",
                    "text": "Стандартный Glassify",
                    "subtext": "Классический баланс прозрачности и размытия",
                },
                {
                    "value": "deep_glass",
                    "text": "Deep Liquid",
                    "subtext": "Глубокое размытие с уплотнённой заливкой",
                },
                {
                    "value": "crystal_clear",
                    "text": "Crystal Clear",
                    "subtext": "Высокая прозрачность и чёткие грани",
                },
            ],
        },
        {
            "type": "divider",
            "text": "Настройки применяются к чатам и клавиатуре",
        },
    ]

    # Регистрируем настройки и callback
    _API.register_settings(settings_schema, callback=_on_setting_changed)

    # Применяем сохранённый ранее стиль
    saved_style = _API.get_setting("material_style", "default")
    _apply_material_style(saved_style)

    # 2. Подписка на изменение ползунка силы стекла
    _API.register_strength_listener(_on_strength_changed)

    # 3. Перехват методов (Hooking)
    # Все хуки, зарегистрированные через _API.hook_method / hook_all_methods,
    # автоматически удаляются при выключении расширения!
    try:
        theme_class = _API.find_class("org.telegram.ui.ActionBar.Theme")
        _API.hook_all_methods(theme_class, "applyTheme", ThemeUpdateHook())
    except Exception as exc:
        _API.log(f"Не удалось установить хук темы: {exc}")


# ==============================================================================
# Точка входа при выгрузке / отключении расширения
# ==============================================================================
def on_unload(api):
    global _API
    api.log("Расширение Custom Glass Accent выгружается...")

    # Сбрасываем кастомные профили материалов на стандартные
    api.set_material_profile(None)

    _API = None