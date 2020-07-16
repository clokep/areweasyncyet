## Analysis of inlineCallback vs. async functions in Synapse

This can be used to generate a graph of the count of `inlineCallback` functions
vs. async functions in the Synapse code base over time.

### How To Run It

Install the requirements: `pip install gitpython`

Run the script to update the results: `python script.py`

View the results locally: `python -m http.server` and open http://localhost:8000

You can see a live version at https://clokep.github.io/areweasyncyet
