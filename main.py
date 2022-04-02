'''
PTT Crawler ver.1
author by adchentc
graduate student of National Yang Ming Chiao Tung University
Major in Computer Science
'''
from PTT_crawler import *


def main():
    print('+======================================+')
    print('|                                      |')
    print('|     Welcome To PTT Crawler Ver.1     |')
    print('|                                      |')
    print('|        **********************        |')
    print('|        | author by adchentc |        |')
    print('|        **********************        |')
    print('|                                      |')
    print('+======================================+')
    start_time = time.time()
    broad_name = input('Enter the BROAD NAME which you want to crawl -> ').lstrip().rstrip()
    broad_URL = get_broad_URL(broad_name)

    total_page_num = input('How many pages do you want to crawl -> ').lstrip().rstrip()
    print('+======================================+')
    print('|   Search for keywords...')
    print('|   (Support more than one keyword, use SPACE to separate. If no, type \'/no\')')
    key_words = input('|   -> ').rstrip()
    print('+======================================+')

    print('...')
    print('...')
    print('...')

    all_posts = crawl(broad_URL, total_page_num, key_words)
    if all_posts is None:
        print('Exit')
    else:
        list_all_posts(all_posts)
        end_time = time.time()
        ans = input('Do you want to save it? (yes/no) -> ').lstrip().rstrip()
        if ans == 'yes':
            save_to_csv(all_posts)

    print('...')
    print('...')
    print('...')

    print('              +==========+')
    print('    +========================+')
    print('+===============================+')
    print('{:.2f} seconds for crawling  ========+'.format(end_time - start_time))
    print('+======================================+')
    print('+======================================+')
    print('|                                      |')
    print('|    Thank you! See you next time.     |')
    print('|                                      |')
    print('+======================================+')


if __name__ == '__main__':
    main()