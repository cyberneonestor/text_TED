from text_TED import *

class TestWorkFile:

    def setup_method(self, method):
        self.work_file = work_file(r'E:\PDF_parser_and_tranlator\files\vaccination.txt', 'eng')

    def test_constructor(self):
        work_file = self.work_file
        assert work_file.path == r'E:\PDF_parser_and_tranlator\files\vaccination.txt'
        assert work_file.dir == 'E:\PDF_parser_and_tranlator\\files\\'
        assert work_file.name == 'vaccination'
        assert work_file.type == 'txt'
        assert work_file.text == []