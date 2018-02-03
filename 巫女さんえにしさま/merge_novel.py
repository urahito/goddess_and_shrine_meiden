import os,sys,codecs,re
import weakref, enum

_files = weakref.WeakValueDictionary()

def share_file(filename, mode):
    if filename not in _files:
        ret = codecs.open(filename, mode, 'utf-8')
    else:
        ret = _files[filename]
    return ret

def get_match_pattern(path, pattern):
    repatter = re.compile(pattern)
    return repatter.match(path)

def get_path(type):
    root = os.path.dirname(os.path.abspath( __file__ ))

    if type == 'paragraph':
        return os.path.join(root,'単品') 
    elif type == 'story':
        return os.path.join(root,'話') 
    elif type == 'chapter':
        return os.path.join(root,'章') 
    return ''

def is_exist_dir(path):
    return os.path.exists(path) and os.path.isdir(path)

def write_text(path, content):    
    try:
        # 書き込み先にutf-8で書き込む
        write_file = share_file(path, 'w')
        for line in content:
            if '.md' in path:
                write_file.write(line + '\r\n')
            else:
                write_file.write(line)
    except IOError as ex:
        print(ex)
        return False

    print('output: ' + path)  
    return True

# ファイルの書き込み
def write_story(path, content):
    # ex)ファイル名頭の'1-1'などをpathから抽出する
    matchOB = get_match_pattern(path, r"[0-9]+-[0-9]+")

    # ファイルのパターンが一致しなければ書き込まない
    if not matchOB:
        return False

    # ex)1-1.txtという形で書き出す
    if '!' in path:
        new_file_name = matchOB.group() + '!.txt'
    else:
        new_file_name = matchOB.group() + '.txt'

    # 1話ごとのフォルダを作る
    new_file_dir = get_path('story')
    if not is_exist_dir(new_file_dir):
        os.mkdir(new_file_dir)
    
    # 1話ごとのファイルのパス
    new_file_path = os.path.join(new_file_dir, new_file_name)

    # 書き込みと結果を返す
    return write_text(new_file_path, content)

def write_chapter(path, content):
    # ex)ファイル名頭の'1'などをpathから抽出する
    matchOB = get_match_pattern(path, r"[0-9]+?")

    # ファイルのパターンが一致しなければ書き込まない
    if not matchOB:
        return False

    # ex)chapter-1.mdという形で書き出す
    new_file_name = 'chapter-' + matchOB.group() + '.md'

    # 1章ごとのフォルダを作る
    new_file_dir = get_path('chapter')
    if not is_exist_dir(new_file_dir):
        os.mkdir(new_file_dir)
    
    # 1章ごとのファイルのパス
    new_file_path = os.path.join(new_file_dir, new_file_name)

    # 書き込みと結果を返す
    return write_text(new_file_path, content)


# ファイルの読み込み
def read_content(path, content):
    # 存在するファイルでなければ処理しない
    if not is_text_file(path):
        return content

    try:
        # ファイルをutf-8で開く
        open_text = share_file(path, 'r')

        # 行ごとにリストに追記する
        for line in open_text.readlines():
            content.append(line)  
        
    except IOError as ex:
        print(ex)
        return content
    
    return content

def is_text_file(path):
    # 存在するファイルでなければ処理しない
    if not (os.path.exists(path) and os.path.isfile(path)):
        return False

    root, ext = os.path.splitext(path)
    return (ext == '.txt')

def merge_story():
    # 固定パスで単品部分を指定
    paragraph_dir = get_path('paragraph')

    # フォルダが存在しなければ処理を停止
    if not is_exist_dir(paragraph_dir) and ('単品' not in paragraph_dir):
        return

    # 読み込みと書き出し
    content = []
    for read_text in os.listdir(paragraph_dir):
        # 読み出し対象のパス
        read_path = os.path.join(paragraph_dir, read_text)

        # テキストファイルであることを確認
        if not is_text_file(read_path):
            continue

        # ファイルの読み込み
        content = read_content(read_path, content)

        # ファイルが1話の終わり(+付き)なら書き込む
        if '+' in read_text:
            if not write_story(read_text, content):
                print('Failed output')

            del content
            content = []

def merge_chapter():
    # 固定パスで「話」のフォルダを指定
    story_dir = get_path('story')

    # フォルダが存在しなければ処理を停止
    if not is_exist_dir(story_dir) and ('話' not in story_dir):
        return

    # 読み込みと書き出し
    content = []
    for read_text in os.listdir(story_dir):
        # 読み出し対象のパス
        read_path = os.path.join(story_dir, read_text)
        
        # テキストファイルであることを確認
        if not is_text_file(read_path):
            continue
    
        # 1話ごとにH1で仮タイトルを付ける
        root, ext = os.path.splitext(read_text)
        content.append('# chapter ' + root + '\r\n\r\n')

        # ファイルの読み込み    
        content = read_content(read_path, content)

        content.append('\r\n')


        # ファイルが1章の終わり(!付き)なら書き込む
        if '!' in read_text:
            if not write_chapter(read_text, content):
                print('Failed output')

            del content
            content = []

def main():
    merge_story()
    merge_chapter()

if __name__ == '__main__':
    main()