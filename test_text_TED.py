from text_TED import *
from text_TED import _ABBREV_parser as ABBREV_parser, _ABBREV_and_termin as ABBREV_and_termin, _change_ABBREVS_on_termins as change_ABBREVS

class TestWorkFile:
    """
    Тестируем методы, относящиеся к получению текста из файлов,
    а так же относящиеся к первичной модификации текста
    """

    def setup_method(self, method):
        self.file_ = SetFile(r'E:/Studing/Programming/Python/Projects/PDF_parser_and_tranlator/main_version/test/initial_text_in_txt_for_tests.txt', 'eng')
        self.rav_text_for_test = ['In 2010, the National Institutes of Health (NIH) contracted with the Institute of Medicine (IOM) to undertake a study and make recommendations “to increase the recognition of pain as a significant public health problem in the United States.” The resulting 2011 IOM report called for a cultural transformation in pain prevention, care, education, and research and recommended development of “a comprehensive population health-level strategy” to address these issues.1 In response to the report, the Assistant Secretary for Health, Department of Health and Human Services (HHS) asked the Interagency Pain Research Coordinating Committee (IPRCC) to oversee creation of this National Pain Strategy (NPS). Experts from a broad array of public and private organizations explored areas identified in the core IOM recommendations—population research, prevention and care, disparities, service delivery and reimbursement, professional education and training, and public awareness and communication. A companion effort is underway to address the IOM’s call for further research to support the cultural transformation.']

    def test_constructor(self):
        work_file = self.file_
        assert work_file.path == r'E:/Studing/Programming/Python/Projects/PDF_parser_and_tranlator/main_version/test/initial_text_in_txt_for_tests.txt'
        assert work_file.dir == 'E:/Studing/Programming/Python/Projects/PDF_parser_and_tranlator/main_version/test/'
        assert work_file.name == 'initial_text_in_txt_for_tests'
        assert work_file.type == 'txt'
        assert work_file.lang == 'eng'
        assert work_file.text == []

    def test_constructor_other_slash(self):
        work_file = SetFile(r'E:\\Studing\\Programming\\Python\\Projects\\PDF_parser_and_tranlator\\files\\vaccination.pdf', 'ru')
        assert work_file.path == r'E:\\Studing\\Programming\\Python\\Projects\\PDF_parser_and_tranlator\\files\\vaccination.pdf'
        assert work_file.dir == r'E:\\Studing\\Programming\\Python\\Projects\\PDF_parser_and_tranlator\\files\\'
        assert work_file.name == 'vaccination'
        assert work_file.type == 'pdf'
        assert work_file.lang == 'ru'
        assert work_file.text == []

    def test_text_extractor_from_txt(self):
        self.file_.extract_text()
        assert self.file_.text == self.rav_text_for_test

    def test_text_extractor_from_pdf(self):
        pdf_file = SetFile(r'E:/Studing/Programming/Python/Projects/PDF_parser_and_tranlator/main_version/test/initial_text_in_pdf_for_tests.pdf', 'eng')
        pdf_file.extract_text()
        assert pdf_file.text == self.rav_text_for_test

    def test_remove_line_beaks(self):
        text_with_line_breaks = SetFile(r'E:/Studing/Programming/Python/Projects/PDF_parser_and_tranlator/main_version/test/text_with_line_breaks.txt', 'eng')
        text_with_line_breaks.extract_text()
        text_with_line_breaks.text = [''.join(text_with_line_breaks.text)]
        assert text_with_line_breaks.remove_line_breaks(text_with_line_breaks.text) == self.rav_text_for_test


class TestABBREVStoTermins:

    def setup_method(self, method):
        self.file_ = SetFile(r'E:/Studing/Programming/Python/Projects/PDF_parser_and_tranlator/main_version/test/initial_text_in_txt_for_tests.txt', 'eng')
        self.file_.text = ['united nations (UN), test driven development (TDD), abra cadabra babra mokabra (ACBM), Russian Federation (RF)']

    def test_ABBREV_parser(self):
        assert ABBREV_parser(self.file_) == ['(UN)', '(TDD)', '(ACBM)', '(RF)']

    def test_ABBREV_and_termin(self):
        assert ABBREV_and_termin(self.file_, ['(UN)', '(TDD)', '(ACBM)', '(RF)']) == {
            'UN': 'united nations',
            'TDD': 'test driven development',
            'ACBM': 'abra cadabra babra mokabra',
            'RF': 'Russian Federation'
        }

    def test_change_ABBREVS(self):
        ABBREVS = {
            'UN': 'united nations',
            'TDD': 'test driven development',
            'ACBM': 'abra cadabra babra mokabra',
            'RF': 'Russian Federation'
        }
        assert change_ABBREVS(self.file_, ABBREVS) == ['united nations (united nations), test driven development (test driven development), abra cadabra babra mokabra (abra cadabra babra mokabra), Russian Federation (Russian Federation)\n']