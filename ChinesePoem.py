#encoding=utf-8
import requests
import re
import jieba
import wordcloud
from matplotlib import pyplot as plt
from wordcloud import WordCloud

def get_lib():
    print('初始化诗人列表...')
    lib_url = 'https://www.gushiwen.org/gushi/quantang.aspx'
    lib_response = requests.get(lib_url)
    lib_response.encoding = 'utf-8'
    lib_html = lib_response.text
    poet_list = re.findall(r'<span><a.*?" t', lib_html)
    poet_name = re.findall(r'卷.*?<', lib_html)
    tmp = []
    for x in poet_list:
        t = 'https://www.gushiwen.org' + x[15:29]
        tmp.append(t)
    poet_list = tmp    
    tmp = []
    for x in poet_name:
        t = x[4:len(x)-1]
        tmp.append(t)
    poet_name = tmp
    print('完成！')
    return poet_name, poet_list

def get_poet_url(name, poet_name, poet_list):
	res = []
    for i in range(len(poet_name)):
        if poet_name[i] == name:
            res.append(poet_list[i])
    return res

def run(target, poet_name, poet_list):
    print("查找中......")
    target_url = get_poet_url(target, poet_name, poet_list)
    target_content = []
    target_info = ''
    text_chap = 0
    if target_url == []:
        print("未找到该诗人！")
        return '',[], [], 0, 0
    else:
        for x in target_url:
            text_chap += 1
            target_res = requests.get(x)
            target_res.encoding = 'utf-8'
            target_html = target_res.text
            if target_info == '':
                target_info = re.findall(r'txtareAuthor.*?。?”?https', target_html, re.S)
                if target_info != []:
                    target_info = target_info[0]
                a = 0
                for x in range(len(target_info)):
                    if target_info[x] == '>':
                        a = x
                        break
                target_info = target_info[a+1:len(target_info)-5]
            target_text = re.findall(r'contson.*?width:1', target_html, re.S)[0]
            target_text = target_text.replace('<br /><br />', '\n')
            target_text = target_text.replace('contson">', '')
            target_text = target_text.replace('</div>', '')
            target_text = target_text.replace('<div style=" width:1', '')
            target_text = target_text.replace('</strong></a>', '')
            rubbish_text = re.findall(r'<a href.*?<strong>', target_text)
            for y in rubbish_text:
                target_text = target_text.replace(y, '')
            rubbish_text2 = re.findall(r'<a.*?a>', target_text)
            for y in rubbish_text2:
                target_text = target_text.replace(y, '')
    #         print(target_text)
            target_content.append(target_text)
    print("查找完成！")
    text_title = []
    text_content = []
    for i in target_content:
        for x in i.split():
            if x[0] == '「':
                text_title.append(x)
            elif x[0] == '卷':
                continue
            else:
                text_content.append(x)
    return target_info, text_title, text_content, text_chap, 1

def print_info(target, target_info, target_chap, text_title, text_content):
    print("===========================================================================================")
    print('诗人简介：')
    if target_info == '':
        print('不详。')
    else:
        print(target_info)
    print("===========================================================================================")
    print("《全唐诗》收录卷数：", target_chap)
    print("《全唐诗》收录作品数：", len(text_title))
    cnt = 0
    stopwords = "，。！？、（）《》【】<>=:+-—"
    for x in text_content:
        for y in x:
            if y not in stopwords:
                cnt += 1
    print("《全唐诗》收录作品总字数：约", cnt, "字")
    print("平均每作品字数：", round(cnt/len(text_title)), "字")

def savetxt(text_content):
    f = open('./PoetryOfTang/tmp.txt', 'w')
    for x in text_content:
        t = ' '.join(jieba.cut(x))
        t = t.split()
        for y in t:
            f.write(y)
            f.write(' ')
    f.close()

def gen_wc(target):
    wc = WordCloud(
        font_path=r"./System/Library/PingFang.ttc",
        background_color='white',
    )
    f = open('./PoetryOfTang/tmp.txt')
    text = f.read()
    f.close()
    wc.generate(text)
    wc.to_file('./PoetryOfTang/' + target + '.png')
    print('词频统计词云：')
    plt.imshow(wc)
    plt.axis('off')
    plt.show()
    print("===========================================================================================")

def word_count(target, num):
    word_lst = []
    word_dict = {}
    stopwords = "，。！？、（）《》【】<>=:+-"
    with open('./PoetryOfTang/tmp.txt') as infile:
        for line in infile:
            for char in line:
                word_lst.append(char)
        for char in word_lst:
            if char not in stopwords:
                if char.strip() not in word_dict:
                    word_dict[char] = 1
                else:
                    word_dict[char] += 1
    lstWords = sorted(word_dict.items(), key=lambda x:x[1],  reverse=True) 
    print("===========================================================================================")
    print("最常用字（前20位）：")
    print ('--------------')
    print ('用字 | 次数')
    print ('--------------')
    for e in lstWords[:num]:
        print ('  %s  | %d' % e)
    print("===========================================================================================")

def main():
    target = input('请输入你要查找的诗人：')
    target_info, text_title, text_content, target_chap, target_find = run(target, poet_name, poet_list)
    if target_find == 1:
        savetxt(text_content)
        print_info(target, target_info, target_chap, text_title, text_content)
        word_count(target, 20)
        gen_wc(target)

if __name__ == '__main__':
	main()