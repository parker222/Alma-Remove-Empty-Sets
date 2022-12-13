# Alma-Remove-Empty-Sets

Python application that removes empty sets from Ex Libris's Alma product. Sets must have been created using the Alma API. Removal of sets also requires an instance specific API key in the config.ini file.

Create a text file of all set names to be removed in the same directory as the application. Each set name MUST be on its own line in the file.

When run the application quieries Alma it verifies that set exists and has zero members. Once verified the set is deleted. The names of deleted sets are printed to an output file in the same directory. Undeleted set names are printed to output files that indicate the nature of the error.
