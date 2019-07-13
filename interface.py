import text_TED


#f = r"E:\Studing\Programming\Python\Projects\PDF_parser_and_tranlator\files\pain_system\eng_The Economic Costs of Pain in the United States.txt"

def files_from_pathfile():
    paths = []
    with open(r"E:\Studing\Programming\Python\Projects\PDF_parser_and_tranlator\files\Pain_system\files_paths.txt", 'r') as f_paths:
        for path in f_paths:
            path = path.replace('\n', '')
            paths.append(path)
    return paths

path = [r'E:\Studing\Programming\Python\Projects\PDF_parser_and_tranlator\files\vaccination.txt']

for f in path:
    work_file = text_TED.work_file(f, 'eng')
    work_file.get_text()
    work_file.text = text_TED.spell_text(work_file)
    work_file.text = text_TED.ABBREVS_to_termins(work_file)
    work_file.text = text_TED.google_translate_text(work_file)
    work_file.save_text(pref='finally')