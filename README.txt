README

a) Team Member
Diyue Xiao (dx2152)
Mengting Wu (mw2987)

b) Files Submitted
README (the readme file)

c) How to run the program

$ python main.py <account_key> <t_es> <t_ec><host>

<account_key> : a string which is the Bing search account key.
<t_es>: a real number which is the specificity threshold (between 0 and 1).
<t_ec>: an integer which is the coverage threshold (t_ec >= 1).
<host>: a string which is the URL of the database to be classified.

d) Internal Design 

Part 1:

Part 2:
	Part 2a:

	Part 2b:

e) Bing Seach Account Key
ACCOUNT_KEY = '7DRu7Sm4WYJGN+T/i6CjP4JDNCOllcOzluR+Uy66ABU='

f) Others
	(1) When constructing content summary from document samples associated with each category, we decide not to include the PDF/PPT files in the retrieved top-4 documents by Bing for each query.
	(2) We decide not to include multiple-word information, corresponding to multiple-word query probes, in the content summaries for Part 2.



