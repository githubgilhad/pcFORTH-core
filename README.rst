
.. image:: MemxFORTHChipandColorfulStack.png
	:width: 250
	:target: MemxFORTHChipandColorfulStack.png

- `memxFORTH-core <#memxforth-core>`__
	- `Interesting words <#interesting-words>`__
	- `Classical words <#classical-words>`__

pcFORTH-core
==============

A small Forth-like core for PC, for geting translation of new FORTH words to in-memory format, with all IMMEDIATE words already processed, so it could be saved into FLASH memory on memxFORTH. PC have a LOT more of memory for this kind of usage.

Based on `memxFORTH-core <https://github.com/githubgilhad/memxFORTH-core>`__

NOTE
====

during bootstrap are needed some hacks

* ( comment in braces ) - once the word `(` (open brace) is defined as IMMEDIATE, it cannot be simply redefined, as `: (` is colon and comment.
	* in jones.4th change `: (` to `: ((` and it should work
* `nick` - on line with `:` colon may be comment in form `( ... "nickname" ... )` and then nickname will be used in \*.inc 
	* SEE (and possibly other words) contining such construction ( here `." BRANCH ( " 0 4 +D DUP2 D@ SWAP . SPACE . ." ) "` ) cannot have it on the colon line 
		* simply add new line somewhere before it

License
-------
GPL 2 or GPL 3 - choose the one that suits your needs.

Author
------
Gilhad - 2025
