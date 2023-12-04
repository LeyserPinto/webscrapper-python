import requests
import time
import csv
import random
import concurrent.futures

from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}

MAX_THREADS = 20

def extractMovieDetails(movieLink):
    time.sleep(random.uniform(0,0.2))
    
    movieSoup = BeautifulSoup(requests.get(movieLink, headers= headers).content, 'html.parser')

    if movieSoup is not None:
        title = None
        date = None
        movieData = movieSoup.find('section', attrs={'class': 'ipc-page-section'})
        
        if movieData is not None:
            # titulo do filme
            title = movieData.find('h1').get_text()
            # ano onde o filme foi publicado       
            date = movieData.find('div', attrs={'class': 'sc-e226b0e3-3 dwkouE'}).select_one('ul.sc-7f1a92f5-4 > li > a').get_text()
            # rating é a nota do filme, por exemplo, 8.6.
            rating = movieSoup.find('span', attrs={'class': 'sc-bde20123-1 cMEQkK'}).get_text() 
            # plot é o texto de sinopse do filme
            plot_text = movieSoup.find('span', attrs={'class': 'sc-466bb6c-2 chnFO'}).get_text().strip() if movieSoup.find(
            'span', attrs={'class': 'sc-466bb6c-2 chnFO'}) else None

            with open('movies.csv', mode='a') as file:
                movieWritter = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                if all([title, date, rating, plot_text]):
                    print(title, date, rating, plot_text)
                    movieWritter.writerow([title, date, rating, plot_text])

def extract_movies(soup):
    # aqui são configurações de hierarquia da página, do ponto de encontro do filme até sua divisão e organização em elementos.
    movies_table = soup.find('div', attrs={'data-testid': 'chart-layout-main-column'}).find('ul')
    movies_table_rows = movies_table.find_all('li')
    movie_links = ['https://imdb.com' + movie.find('a')['href'] for movie in movies_table_rows]

    threads = min(MAX_THREADS, len(movie_links))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(extractMovieDetails, movie_links)

def main():
    startTime = time.time()

    # IMDB Most Popular Movies - 100 movies
    popular_movies_url = 'https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm'
    response = requests.get(popular_movies_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Main function to extract the 100 movies from IMDB Most Popular Movies
    extract_movies(soup)

    end_time = time.time()
    print('Total time taken: ', end_time - startTime)


if __name__ == '__main__':
    main()