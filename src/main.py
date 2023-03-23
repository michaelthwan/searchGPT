from SearchGPTService import SearchGPTService
import yaml
import os
from Util import get_project_root
import gettext


if __name__ == '__main__':
    config = None

    with open(os.path.join(get_project_root(), 'src/config/config.yaml'), encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    locale = config.get('system').get('locale')
    tr = gettext.translation('base', localedir='locales', languages=[locale])
    _ = tr.gettext

    search_text = _('the source of dark energy')
    search_gpt_service = SearchGPTService()
    response_text, source_text, data_json = search_gpt_service.query_and_get_answer(search_text=search_text)
    print()
