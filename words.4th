: '' WORD FIND h2cw ;				\ ( "doubletick" )

: HIDE						\ DEFWORD w_hide, 0, "HIDE", f_docol		; HIDE WORD hide/unhide the word
	WORD FIND HIDDEN ;			\	.long w_word_cw,w_find_cw,w_hidden_cw,w_exit_cw


: IF IMMEDIATE					\ DEFWORD w_if, FLG_IMMEDIATE, "IF", f_docol		; do if not zero
	' 0BRANCH ,				\	.long w_tick_cw, w_0branch_cw,w_comma_cw	; if zero, branch
	HERE D@ 0 0 ,				\	.long var_HERE_cw, w_DoubleAt_cw, w_lit2_cw,0,w_comma_cw	; save this pos, fill 0 for now
	;					\	.long w_exit_cw

: FI IMMEDIATE					\ DEFWORD w_fi, FLG_IMMEDIATE, "FI", f_docol		; fi - end of IF
	DUP2 HERE D@ SWAP2 -D SWAP2 !D ;	\	.long w_dup_D_cw, var_HERE_cw, w_DoubleAt_cw, w_swap_D_cw, w_minus_D_cw, w_swap_D_cw,w_StoreDouble_cw,w_exit_cw

: THEN IMMEDIATE				\ DEFWORD w_then, FLG_IMMEDIATE, "THEN", f_docol		; fi - end of IF
	[ '' FI , ] ;					\	.long w_fi_cw, w_exit_cw

: ELSE IMMEDIATE				\ DEFWORD w_else, FLG_IMMEDIATE, "ELSE", f_docol		; else do this
	' BRANCH ,				\	.long w_tick_cw, w_branch_cw,w_comma_cw		; like in IF, but branch everytime
	HERE D@ 0 ,				\	.long var_HERE_cw, w_DoubleAt_cw, w_lit2_cw, 0,w_comma_cw	; save this pos, fill 0 for now
	SWAP2 [ '' FI , ] ;				\	.long w_swap_D_cw, w_fi_cw, w_exit_cw		; swap this and IFs address and fill it like FI

: BEGIN IMMEDIATE				\	DEFWORD w_begin, FLG_IMMEDIATE, "BEGIN", f_docol	; BEGIN loop-part condition UNTIL
	HERE D@ ;				\	.long var_HERE_cw, w_DoubleAt_cw, w_exit_cw

: UNTIL IMMEDIATE 				\ DEFWORD w_until, FLG_IMMEDIATE, "UNTIL", f_docol	; BEGIN loop-part condition UNTIL
	' 0BRANCH ,				\	.long w_tick_cw, w_0branch_cw,w_comma_cw
	HERE D@ -D ,				\	.long var_HERE_cw, w_DoubleAt_cw, w_minus_D_cw, w_comma_cw
	;					\	.long w_exit_cw

: WHILE IMMEDIATE				\ DEFWORD w_while, FLG_IMMEDIATE, "WHILE", f_docol	; BEGIN condition WHILE loop-part REPEAT
	[ '' IF , ] ;					\	.long w_if_cw,w_exit_cw

: REPEAT IMMEDIATE 				\ BEGIN condition WHILE loop-part REPEAT
	' BRANCH ,				\ compile BRANCH
	SWAP2					\ get the original offset (from BEGIN)
	HERE D@ -D ,				\ and compile it after BRANCH
	DUP2
	HERE D@ SWAP2 -D			\ calculate the offset2
	SWAP2 !D ;				\ and back-fill it in the original location

: FORGET					\ DEFWORD w_forget,0,"FORGET",f_docol			; forget word (and all after)
	WORD FIND				\	.long w_word_cw, w_find_cw
\	DUP2 0x800000 ==D IF EXIT FI		\    check, if the WORD exist 	 \ cannot use IMMEDIATE words in asm.compile
\	DUP2 0x800000 <>D 
\	0BRANCH \'3 DROP2 RETURN		\ better check
	DUP2 ISNULL 
	IF DROP2 RETURN	FI	\ better check for NULLs
	DUP2 D@ LAST !D				\ set LAST header to value of next field
	HERE !D ;				\ free RAM memory

: ascii 					\ ( -- ) emits 00..FF chars
	0					\ loop variable
	BEGIN					\ BEGIN - target for 0BRANCH
	DUP EMIT 				\ EMIT current char
	 1 +					\ i++
	DUP 100 - 0= 				\ ? equal to 256?
	UNTIL		 			\ if no, repeat (branch to BEGIN)
	DROP ;					\ cleanup
