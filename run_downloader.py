from selenium import webdriver
import urllib.parse
import time
from selenium.common.exceptions import NoSuchElementException
import re
import pandas as pd
import sys
class IeeeDownloader:

    def __init__(self, search_name, year_range):
       self.search_name = search_name
       self.year_range = year_range
       self.browser=webdriver.Chrome() # 驅動chrome
       self.paper_elements=[]
    def run_crawl(self):
        self.base="https://ieeexplore.ieee.org/search/searchresult.jsp?"
        self.querystring=self.base+"queryText="+urllib.parse.quote(self.search_name)+"&highlight=true&returnFacets=ALL&returnType=SEARCH&ranges="+self.year_range+"_Year"
        print(self.querystring)
        self.browser.get(self.querystring) # 跳轉到目標頁面
        time.sleep(5) #
        js = 'window.scrollTo(0, document.body.scrollHeight);'
        self.browser.execute_script(js)
        load_btn = "//button[@class='loadMore-btn']"
        while(1):
            try:
                # Insert your scraping action here
                python_button=self.browser.find_element_by_xpath(load_btn)
                python_button.click()
                time.sleep(7)
                js = 'window.scrollTo(0, document.body.scrollHeight);'
                self.browser.execute_script(js)
            except NoSuchElementException:
                print("Done finding button")
                break
        # 開始下載
        print("begin crawling!!!")
        paper_list = self.browser.find_elements_by_css_selector('div.List-results-items')
        print("totally ",len(paper_list))
        # base_link='http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber='
        # deal with data
        for paper in paper_list:
            paper_info={}
            # download_link=paper.find_element_by_xpath("//*[@data-artnum]")
            # artnum=download_link.get_attribute('data-artnum')
            download_link=paper.find_element_by_class_name('u-flex-display-flex').find_element_by_tag_name("a").get_attribute('href')
            # print(str(download_link).encode("utf8").decode("cp950", "ignore"))
            paper_info['link']=download_link
            title=paper.find_element_by_tag_name("h2").text
            paper_info['title']=str(title).encode("utf8").decode("cp950", "ignore")
            authors=paper.find_element_by_class_name('author').text
            paper_info['authors']=str(authors).encode("utf8").decode("cp950", "ignore")
            # print(authors.encode("utf8").decode("cp950", "ignore"))
            conference=paper.find_element_by_class_name('description').find_element_by_tag_name("a").text
            paper_info['conference']=str(conference).encode("utf8").decode("cp950", "ignore")
            # print(conference.encode("utf8").decode("cp950", "ignore"))
            publisher_info_container=paper.find_element_by_class_name('publisher-info-container').text
            paper_info['publisher-info']=publisher_info_container
            year=publisher_info_container.split('|')[0]
            year=str(year).encode("utf8").decode("cp950", "ignore")
            year=re.findall(r"\d+",year)[0]
            paper_info['year']=year
            description=paper.find_element_by_class_name('description').text.encode("utf8").decode("cp950", "ignore")
            cite_number=re.findall(r"Papers [(]\d+[)]",description)
            # print(description.encode("utf8").decode("cp950", "ignore"))
            if(cite_number):
                cite_number=re.findall(r"\d+",cite_number[0])
                paper_info['cite_number']=int(cite_number[0])
            else:
                paper_info['cite_number']=0
            self.paper_elements.append(paper_info)
    def save_to_excel(self):
        df = pd.DataFrame(columns=self.paper_elements[0].keys())
        for paper in self.paper_elements:
            s = pd.Series(paper)
            df = df.append(s, ignore_index=True)
        # save to excel
        file_name=self.search_name+" "+self.year_range
        df.to_excel(file_name+".xlsx",index=False)
    def driver_close(self):
        self.browser.close()

if __name__=="__main__":
    # year_range 格式:2009_2020
    # search_name: string
    year_range=sys.argv[1]
    search_name=sys.argv[2]
    ieee=IeeeDownloader(search_name,year_range)

    ieee.run_crawl()
    ieee.save_to_excel()
    ieee.driver_close()