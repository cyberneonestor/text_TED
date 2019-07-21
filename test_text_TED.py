from text_TED import *

class TestWorkFile:

    def setup_method(self, method):
        self.file_ = work_file(r'E:/Studing/Programming/Python/Projects/PDF_parser_and_tranlator/main_version/test/initial_text_in_txt_for_tests.txt', 'eng')
        self.rav_text_for_test = ['In 2010, the National Institutes of Health (NIH) contracted with the Institute of Medicine (IOM) to undertake a study and make recommendations “to increase the recognition of pain as a significant public health problem in the United States.” The resulting 2011 IOM report called for a cultural transformation in pain prevention, care, education, and research and recommended development of “a comprehensive population health-level strategy” to address these issues.1 In response to the report, the Assistant Secretary for Health, Department of Health and Human Services (HHS) asked the Interagency Pain Research Coordinating Committee (IPRCC) to oversee creation of this National Pain Strategy (NPS). Experts from a broad array of public and private organizations explored areas identified in the core IOM recommendations—population research, prevention and care, disparities, service delivery and reimbursement, professional education and training, and public awareness and communication. A companion effort is underway to address the IOM’s call for further research to support the cultural transformation.']

    def test_constructor(self):
        work_file = self.file_
        assert work_file.path == r'E:/Studing/Programming/Python/Projects/PDF_parser_and_tranlator/main_version/test/initial_text_in_txt_for_tests.txt'
        assert work_file.dir == 'E:/Studing/Programming/Python/Projects/PDF_parser_and_tranlator/main_version/test/'
        assert work_file.name == 'initial_text_in_txt_for_tests'
        assert work_file.type == 'txt'
        assert work_file.text == []

    def test_text_extractor_from_txt(self):
        self.file_.get_text()
        assert self.file_.text == self.rav_text_for_test

    def test_text_extractor_from_pdf(self):
        pdf_file = work_file(r'E:/Studing/Programming/Python/Projects/PDF_parser_and_tranlator/main_version/test/initial_text_in_pdf_for_tests.pdf', 'eng')
        pdf_file.get_text()
        assert pdf_file.text == self.rav_text_for_test