Class Structure Initializer for Ghidra
======================================

Execute when `currentLocation` is the beginning of a recognized Visual Studio vftable (we rely on the auto-generated plate comment).

The script will generate initial structures and updates symbol information. 

This is more of a PoC than a generic tool, but I hope it will provide some useful API examples and ways to represent classes in Ghidra. Inspired by:

* http://hwreblog.com/projects/ghidra.html
* https://insights.sei.cmu.edu/sei_blog/2019/07/using-ooanalyzer-to-reverse-engineer-object-oriented-code-with-ghidra.html

The code also highlights some inconveniences in the Ghidra API. If you have cleaner solutions, please open an Issue or a PR!

**Update**: this looks like a parallel effort to the more mature [Ghidra-Cpp-Class-Analyzer](https://github.com/astrelsky/Ghidra-Cpp-Class-Analyzer) extension - consider taking a look over there!
