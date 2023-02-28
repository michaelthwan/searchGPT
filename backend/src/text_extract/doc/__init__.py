from .docx_svc import docx_extract_svc
from .ppt_svc import ppt_extract_svc

support_doc_type = ['doc', 'docx', 'ppt', 'pptx']
doc_extract_svc_map = {
    'doc': docx_extract_svc,
    'docx': docx_extract_svc,
    'ppt': ppt_extract_svc,
    'pptx': ppt_extract_svc
}
