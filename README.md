## Analysis of inlineCallback vs. async functions in Synapse

This can be used to generate a graph of the count of `inlineCallback` functions
vs. async functions in the Synapse code base over time.

### How To Run It

Install the requirements: `pip install gitpython`

Check out Synapse into this directory: `git clone git@github.com:matrix-org/synapse.git`

Run the script to update the results: `python script.py`

View the results locally: `python -m http.server` and open http://localhost:8000

You can see a live version at https://patrick.cloke.us/areweasyncyet/

Python >= 3.7 required.