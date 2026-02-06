import os
import json
from flask import session, request, current_app

class I18nService:
    def __init__(self, app=None):
        self._translations = {}
        self._default_lang = 'fr'
        self._supported_langs = ['fr', 'en']
        if app:
            self.init_app(app)

    def init_app(self, app):
        self._load_translations(app)

        # Register context processor
        app.context_processor(self.context_processor)

    def _load_translations(self, app):
        # Check standard locations
        possible_paths = [
            os.path.join(app.root_path, 'lang'),
            os.path.join(os.getcwd(), 'lang'),
            os.path.join(os.path.dirname(app.root_path), 'lang')
        ]

        lang_dir = None
        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                lang_dir = path
                break

        if not lang_dir:
            print("Warning: 'lang' directory not found.")
            return

        for lang in self._supported_langs:
            file_path = os.path.join(lang_dir, f'{lang}.json')
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self._translations[lang] = json.load(f)
                except Exception as e:
                    print(f"Error loading {lang}.json: {e}")
                    self._translations[lang] = {}
            else:
                self._translations[lang] = {}

    def get_locale(self):
        # 1. Check session
        if session.get('lang') in self._supported_langs:
            return session['lang']

        # 2. Check header
        best_match = request.accept_languages.best_match(self._supported_langs)
        if best_match:
            return best_match

        # 3. Default
        return self._default_lang

    def get_text(self, key, **kwargs):
        lang = self.get_locale()
        keys = key.split('.')

        # Try to fetch from translations
        data = self._translations.get(lang, {})
        for k in keys:
            if isinstance(data, dict):
                data = data.get(k)
            else:
                data = None
                break

        # Fallback to default lang if missing
        if data is None and lang != self._default_lang:
            data = self._translations.get(self._default_lang, {})
            for k in keys:
                if isinstance(data, dict):
                    data = data.get(k)
                else:
                    data = None
                    break

        # Return key if still missing
        if data is None:
            return f"[{key}]"

        if isinstance(data, str) and kwargs:
            try:
                return data.format(**kwargs)
            except:
                return data

        return data

    def context_processor(self):
        return dict(_=self.get_text, get_locale=self.get_locale)

i18n = I18nService()
