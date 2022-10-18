import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    #trans_model = copy.deepcopy(corpus)
    trans_model = dict()
    links = corpus[page]

    #check whether current page links to any others. If not, set equal probability for next page between all pages.
    if links == None:
        print("none hit")
        
        for pagename in corpus:

            trans_model[pagename] = 1 / len(corpus)
        
        return trans_model

    #If links to other pages apply relative probability
    else:

        for pagename in corpus:

            #If page is linked to, probability that link is followed plus probability of random page selected from damping factor
            if pagename in links:

                trans_model[pagename] = damping_factor / len(links) + (1 - damping_factor) / len(corpus)
            
            #If page not linked to, probability that random page is selected from damping factor
            else:
                
                trans_model[pagename] = (1 - damping_factor) / len(corpus)

        return trans_model        




    


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    #Set first sample as a random page
    samples = [random.choice(list(corpus.keys()))]

    #For next n-1 samples use transition model to determine next sample
    for i in range(n-1):

        trans_model = transition_model(corpus, samples[-1], damping_factor)

        random_sample = random.choices(list(trans_model.keys()), list(trans_model.values()))[0] 

        samples.append(random_sample)

    #Initialize sample page rank dictionary
    sample_pr = dict()
    
    for pagename in corpus:

        sample_pr[pagename] = float(samples.count(pagename)) / float(n)

    return sample_pr



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    iterate_pr = dict()
    
    #Star by assigning all equal page rank as 1 / number of pages in corpus
    for pagename in corpus:
                
        iterate_pr[pagename] = 1 / len(corpus)
        
        #If a page has no links, interpret as having one link to each page
        if len(corpus[pagename]) == 0:
            corpus[pagename] = set(corpus.keys())
    
    #Iterate until converged
    while True:

        convergence_count = 0

        for pagename in corpus:

            #Make copy of previous rank to check for convergence
            previous_rank = copy.deepcopy(iterate_pr[pagename])
            
            #First part of iterative equation
            new_rank = (1 - damping_factor) / len(corpus)
            linked_pages = list()

            #Check all pages for a link to the current page, if link exists add to list of linked pages
            for previous_page in corpus:

                if pagename in corpus[previous_page]:

                    linked_pages.append(previous_page)
            
            
            #Initialize and carry out summation part of equation
            summation = 0 

            for link in linked_pages:

                #summation of page rank of previous linked page divided by number of links on that page
                summation += iterate_pr[link] / len(corpus[link])
            
            summation *= damping_factor
            new_rank += summation
            iterate_pr[pagename] = new_rank

            if abs(new_rank - previous_rank) > 0.001:
                convergence_count += 1

        if convergence_count == 0:
            break

    return iterate_pr                


          



if __name__ == "__main__":
    main()
