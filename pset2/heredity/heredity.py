import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    prob_tally = dict()
    #For every person in people, check whether they have parents listed
    for person in people:

        #If no parents, use probability distribution from PROBS
        if people[person]["mother"] == None:

            if person in two_genes:
                genes = 2

            elif person in one_gene:
                genes = 1 

            else:
                genes = 0
            
            #Probability this person has x copies of the gene
            prob_tally[person] = PROBS["gene"][genes]

            if person in have_trait:
                trait = True
            
            else:
                trait = False

            #Probabilty of gene being present or not given x copies of gene
            prob_tally[person] *= PROBS["trait"][genes][trait]


        #If person has parents listed
        else:
            
            mother = people[person]["mother"]
            father = people[person]["father"]

            if mother in two_genes:
                mother_genes = 2

            elif mother in one_gene:
                mother_genes = 1

            else:
                mother_genes = 0

            if father in two_genes:
                father_genes = 2

            elif father in one_gene:
                father_genes = 1

            else:
                father_genes = 0
            
            #Calculate probability of receiving one gene from mother or father
            prob_gene_from_mother = (mother_genes / 2 * (1 - PROBS["mutation"])) + ((1 - mother_genes / 2) * PROBS["mutation"])
            prob_gene_from_father = (father_genes / 2 * (1 - PROBS["mutation"])) + ((1 - mother_genes / 2) * PROBS["mutation"])
   

            if person in two_genes:
                
                genes = 2
                prob_tally[person] = prob_gene_from_mother * prob_gene_from_father

            elif person in one_gene:

                genes = 1
                prob_tally[person] = prob_gene_from_mother * (1 - prob_gene_from_father) + (1 - prob_gene_from_mother) * prob_gene_from_father

            else:

                genes = 0
                prob_tally[person] = (1 - prob_gene_from_mother) * (1 - prob_gene_from_father)

            
            if person in have_trait:
                trait = True
            else:
                trait = False 

            #If no trait data already, use conditional probability from PROBS
            if people[person]["trait"] == None:

                prob_tally[person] *= PROBS["trait"][genes][trait]

    joint_prob = 1

    for person in prob_tally:

        joint_prob *= prob_tally[person]   

    return joint_prob                 



def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:

        if person in two_genes:
            genes = 2
        
        elif person in one_gene:
            genes = 1

        else:
            genes = 0
        
        if person in have_trait:
            trait = True

        else:
            trait = False

        probabilities[person]["gene"][genes] += p
        probabilities[person]["trait"][trait] += p




def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:

        for distribution in probabilities[person]:

            sum_prob = 0

            #Sum together probabilities
            for item in probabilities[person][distribution]:

                sum_prob += probabilities[person][distribution][item]

            #Calculate scaling factor alpha
            alpha = 1 / sum_prob

            #Multiply each item by scaling factor
            for item in probabilities[person][distribution]:

                probabilities[person][distribution][item] *= alpha
            


if __name__ == "__main__":
    main()