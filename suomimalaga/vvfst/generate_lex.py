# -*- coding: utf-8 -*-

# Copyright 2007 - 2012 Harri Pitkänen (hatapitk@iki.fi)
# Program to generate lexicon files for Suomi-malaga Voikko edition

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys
sys.path.append("common")
import hfconv
import generate_lex_common
import voikkoutils
import xml.dom.minidom
import codecs
from string import rfind
from xml.dom import Node

flag_attributes = voikkoutils.readFlagAttributes(generate_lex_common.VOCABULARY_DATA + u"/flags.txt")

# Get command line options
OPTIONS = generate_lex_common.get_options()

# Inflection class map
CLASSMAP = hfconv.compileClassmapREs(hfconv.modern_classmap)

# No special vocabularies are built for Voikko
generate_lex_common.SPECIAL_VOCABULARY = []

vocabularyFileSuffixes = [u"ep", u"ee", u"es", u"em", u"t", u"nl", u"l", u"n", u"h", u"p", u"a", u"s", u"c"]
vocabularyFiles = {}
for fileSuffix in vocabularyFileSuffixes:
	vocFile = codecs.open(OPTIONS["destdir"] + u"/joukahainen-" + fileSuffix + u".lexc", 'w', 'UTF-8')
	vocFile.write(u"! This is automatically generated intermediate lexicon file for\n")
	vocFile.write(u"! VVFST morphology. The original source data is\n")
	vocFile.write(u"! distributed under the GNU General Public License, version 2 or\n")
	vocFile.write(u"! later, as published by the Free Software Foundation. You should\n")
	vocFile.write(u"! have received the original data, tools and instructions to\n")
	vocFile.write(u"! generate this file (or instructions to obtain them) wherever\n")
	vocFile.write(u"! you got this file from.\n\n")
	vocFile.write(u"LEXICON Joukahainen_" + fileSuffix + u"\n")
	vocabularyFiles[fileSuffix] = vocFile


def frequency(word):
	fclass = word.getElementsByTagName("fclass")
	if len(fclass) == 0: return 7
	return int(generate_lex_common.tValue(fclass[0]))

# Check the style flags of the word according to current options.
# Returns True if the word is acceptable, otherwise returns false.
def check_style(word):
	global OPTIONS
	for styleE in word.getElementsByTagName("style"):
		for style in generate_lex_common.tValues(styleE, "flag"):
			if style == "foreignloan":
				continue
			if not style in OPTIONS["style"]: return False
	return True

# Returns True if the word is acceptable according to its usage flags.
def check_usage(word):
	global OPTIONS
	wordUsage = word.getElementsByTagName("usage")
	if len(wordUsage) == 0: return True
	for usageE in wordUsage:
		for usage in generate_lex_common.tValues(usageE, "flag"):
			if usage in OPTIONS["extra-usage"]: return True
	return False

# Returns VFST word class for given word in Joukahainen
def get_vfst_word_class(j_wordclasses):
	if "pnoun_place" in j_wordclasses: return u"[Lep]"
	if "pnoun_firstname" in j_wordclasses: return u"[Lee]"
	if "pnoun_lastname" in j_wordclasses: return u"[Les]"
	if "pnoun_misc" in j_wordclasses: return u"[Lem]"
	if "verb" in j_wordclasses: return u"[Lt]"
	if "adjective" in j_wordclasses and "noun" in j_wordclasses: return u"[Lnl]"
	if "adjective" in j_wordclasses: return u"[Ll]"
	if "noun" in j_wordclasses: return u"[Ln]"
	if "interjection" in j_wordclasses: return u"[Lh]"
	if "prefix" in j_wordclasses: return u"[Lp]"
	if "abbreviation" in j_wordclasses: return u"[La]"
	if "adverb" in j_wordclasses: return u"[Ls]"
	if "conjunction" in j_wordclasses: return u"[Lc]"
	return None

# Returns a string describing the structure of a word, if necessary for the spellchecker
# or hyphenator
def get_structure(wordform, vfst_word_class, alku):
	needstructure = False
	ispropernoun = vfst_word_class[0:3] == u'[Le'
	structstr = u'[Xr]'
	oldAlku = alku
	newAlku = u""
	if vfst_word_class == u'[La]':
		i = u"j"
		p = u"q"
	else:
		i = u"i"
		p = u"p"
	for idx in range(len(wordform)):
		c = wordform[idx]
		if c == u'-':
			structstr = structstr + u"-="
			if (len(oldAlku) > 0):
				newAlku = newAlku + u'-[Bm]'
				oldAlku = oldAlku[1:]
		elif c == u'|':
			structstr = structstr
		elif c == u'=':
			structstr = structstr + u"="
			newAlku = newAlku + u"[Bm]"
		elif c == u':':
			structstr = structstr + u":"
			needstructure = True
			if (len(oldAlku) > 0):
				newAlku = newAlku + u':'
				oldAlku = oldAlku[1:]
		elif c.isupper():
			structstr = structstr + i
			if not (ispropernoun and idx == 0):
				needstructure = True
			if (len(oldAlku) > 0):
				newAlku = newAlku + oldAlku[0]
				oldAlku = oldAlku[1:]
		else:
			structstr = structstr + p
			if ispropernoun and idx == 0:
				needstructure = True
			if (len(oldAlku) > 0):
				newAlku = newAlku + oldAlku[0]
				oldAlku = oldAlku[1:]
	if needstructure:
		returnedLength = len(structstr)
		while structstr[returnedLength - 1] == p:
			returnedLength = returnedLength - 1
		return (structstr[0:returnedLength] + u'[X]', alku)
	else:
		return (u"", newAlku)

def get_diacritics(word, altforms, vfst_word_class):
	diacritics = []
	for group in word.childNodes:
		if group.nodeType != Node.ELEMENT_NODE:
			continue
		for flag in group.childNodes:
			if flag.nodeType != Node.ELEMENT_NODE:
				continue
			if flag.tagName != "flag":
				continue
			flagName = flag.firstChild.wholeText
			if flagName == u"ei_yks":
				diacritics.append(u"@P.EI_YKS.ON@")
			elif flagName == u"ysj":
				diacritics.append(u"@R.YS_ALKANUT@")
			elif flagName == u"inen":
				diacritics.append(u"@P.INEN_SALLITTU.ON@")
			elif flagName == u"ei_inen":
				diacritics.append(u"@P.INEN_KIELLETTY.ON@")
			elif flagName == u"ei_mainen":
				diacritics.append(u"@P.EI_MAINEN.ON@")
			elif flagName == u"ei_lainen":
				diacritics.append(u"@P.EI_LAINEN.ON@")
			elif flagName == u"ei_vertm":
				diacritics.append(u"@P.EI_VERTM.ON@")
			elif flagName == u"ym3":
				diacritics.append(u"@P.VAIN_YM3.ON@")
			elif flagName == u"yt":
				diacritics.append(u"@P.YKSITEKIJÄINEN.ON@")
			elif flagName == u"geo_suffix":
				diacritics.append(u"@C.PAIKANNIMEN_JL@")
			if flagName in [u"ei_ys", u"ei_ysa"]:
				diacritics.append(u"@P.YS_EI_JATKOA.ON@")
			if flagName in [u"ei_ys", u"ei_ysj"]:
				diacritics.append(u"@D.YS_ALKANUT@")
	if vfst_word_class in [u"[Ln]", u"[Lnl]"] and (altforms[0].endswith(u"lainen") or altforms[0].endswith(u"läinen")):
		diacritics.append(u"@P.LAINEN.ON@@C.LAINEN_VAADITTU@@C.VAIN_NIMISANA@")
	return diacritics

def get_info_flags(word):
	flags = u""
	for group in word.childNodes:
		if group.nodeType != Node.ELEMENT_NODE:
			continue
		for flag in group.childNodes:
			if flag.nodeType != Node.ELEMENT_NODE:
				continue
			if flag.tagName != "flag":
				continue
			flagName = flag.firstChild.wholeText
			if flagName == u"paikannimi_ulkopaikallissijat":
				flags = flags + u"[Ipu]"
			elif flagName == u"paikannimi_sisäpaikallissijat":
				flags = flags + u"[Ips]"
			elif flagName == u"foreignloan":
				flags = flags + u"[Isf]"
			elif flagName == u"el_altark":
				flags = flags + u"[De]"
			elif flagName == u"geo_suffix":
				flags = flags + u"[Ica]"
			elif flagName == u"org_suffix":
				flags = flags + u"[Ion]"
			elif flagName == u"free_suffix":
				flags = flags + u"[Ivj]"
			elif flagName == u"require_following_a":
				flags = flags + u"[Ira]"
			elif flagName == u"require_following_ma":
				flags = flags + u"[Irm]"
	return flags

def get_vfst_class_prefix(vfst_class):
	if vfst_class == u"[Ln]":
		return u"Nimisana"
	elif vfst_class == u"[Lee]":
		return u"Etunimi"
	elif vfst_class == u"[Lep]":
		return u"Paikannimi"
	elif vfst_class == u"[Les]":
		return u"Sukunimi"
	elif vfst_class == u"[Lem]":
		return u"Nimi"
	elif vfst_class == u"[Ll]":
		return u"Laatusana"
	elif vfst_class == u"[Lnl]":
		return u"NimiLaatusana"
	else:
		return u""

def vowel_type_for_derived_verb(wordform):
	for char in reversed(wordform):
		if char in u"yäö":
			return u"@P.V_SALLITTU.E@"
		if char in u"uao":
			return u"@P.V_SALLITTU.T@"
		if char in u"]":
			break
	return u"@P.V_SALLITTU.T@"

def get_prefix_jatko(word, altform):
	flags = generate_lex_common.get_flags_from_group(word, u"compounding")
	prefixJatko = u""
	for flag in sorted(flags):
		if flag in [u"eln", u"ell", u"elt", u"eltj"]:
			prefixJatko = prefixJatko + flag
	if altform.endswith(u"-"):
		prefixJatko = prefixJatko + u"H"
	return prefixJatko

def get_adverb_jatko(word, altform):
	flags = generate_lex_common.get_flags_from_group(word, u"inflection")
	loppu = True
	adverbJatko = u""
	for flag in sorted(flags):
		if flag in [u"liitesana", u"ulkopaikallissijat_yks"]:
			adverbJatko = adverbJatko + flag.title()
		elif flag == u"omistusliite":
			if altform[-1] in u"aäe" and altform[-1] != altform[-2]:
				adverbJatko = adverbJatko + u"OlV"
			else:
				adverbJatko = adverbJatko + u"Omistusliite"
		elif flag == u"required":
			loppu = False;
	if loppu:
		adverbJatko = "Loppu" + adverbJatko
	return adverbJatko

def get_abbreviation_jatko(word, wordform):
	flags = generate_lex_common.get_flags_from_group(word, u"inflection")
	if wordform.endswith(u".") or u"none" in flags:
		return u"PisteellisenLyhenteenJatko"
	else:
		return u"Lyhenne"

def handle_word(word):
	global OPTIONS
	global CLASSMAP
	# Drop words that are not needed in the Voikko lexicon
	# but only if not generating Sukija lexicon.
	if generate_lex_common.has_flag(word, "not_voikko") and not OPTIONS["sukija"]: return
	if not check_style(word): return
	if not check_usage(word): return
	if frequency(word) >= OPTIONS["frequency"] + 1: return
	if frequency(word) == OPTIONS["frequency"] and generate_lex_common.has_flag(word, "confusing"): return
	
	# Get the inflection class. Exactly one inflection class is needed
	voikko_infclass = None
        if OPTIONS["sukija"]:
                for infclass in word.getElementsByTagName("infclass"):
                        if infclass.getAttribute("type") == "historical":
                                voikko_infclass = generate_lex_common.tValue(infclass)
                                if voikko_infclass == u"banaali":   # Banaali taipuu kuten paperi.
                                        voikko_infclass = u"paperi"
                                elif voikko_infclass == u"pasuuna":
                                        voikko_infclass = u"peruna"
                                if voikko_infclass not in [u"aavistaa-av1", u"arvelu", u"arvelu-av1", u"haravoida-av2", u"karahka", u"matala",
                                                           u"paperi", u"paperi-av1", u"peruna"]:
                                        voikko_infclass = None
                                break
        if voikko_infclass == None:
                for infclass in word.getElementsByTagName("infclass"):
                        if infclass.getAttribute("type") != "historical":
                                voikko_infclass = generate_lex_common.tValue(infclass)
                                break
	if voikko_infclass == u"poikkeava": return
	
	# Get the word classes
	wordclasses = generate_lex_common.tValues(word.getElementsByTagName("classes")[0], "wclass")
	if wordclasses[0] not in [u"interjection", u"prefix", u"abbreviation", u"conjunction", u"adverb"] and voikko_infclass == None:
		return
	vfst_word_class = get_vfst_word_class(wordclasses)
	if vfst_word_class == None: return
	
	# Get diacritics
	altforms = generate_lex_common.tValues(word.getElementsByTagName("forms")[0], "form")
	diacritics = reduce(lambda x, y: x + y, get_diacritics(word, altforms, vfst_word_class), u"")
	
	# Get forced vowel type
	if voikko_infclass == None and vfst_word_class != u"[La]":
		forced_inflection_vtype = voikkoutils.VOWEL_DEFAULT
	else:
		inflectionElement = word.getElementsByTagName("inflection")
		if len(inflectionElement) > 0:
			forced_inflection_vtype = generate_lex_common.vowel_type(inflectionElement[0])
		else:
			forced_inflection_vtype = voikkoutils.VOWEL_DEFAULT
	
	# Construct debug information
	debug_info = u""
	if OPTIONS["sourceid"]:
		debug_info = u'[Xs]%s[X]' % word.getAttribute("id")[1:].replace(u"0", u"%0")
	
	infoFlags = get_info_flags(word)
	
	# Process all alternative forms
	singlePartForms = []
	multiPartForms = []
	for altform in altforms:
		wordform = altform.replace(u'|', u'').replace(u'=', u'')
		if len(altform) == len(wordform.replace(u'-', u'')):
			singlePartForms.append(altform)
		else:
			multiPartForms.append(altform)
		(alku, jatko) = generate_lex_common.get_malaga_inflection_class(wordform, voikko_infclass, wordclasses, CLASSMAP)
		if vfst_word_class == u"[La]":
			jatko = get_abbreviation_jatko(word, altform)
		elif vfst_word_class == u"[Ls]":
			jatko = get_adverb_jatko(word, altform)
		else:
			jatko = jatko.title()
		if vfst_word_class in [u"[Ls]", u"[Lc]", u"[Lh]"]:
			for element in word.getElementsByTagName(u"baseform"):
				wordform = generate_lex_common.tValue(element)
		if forced_inflection_vtype == voikkoutils.VOWEL_DEFAULT:
			vtype = voikkoutils.get_wordform_infl_vowel_type(altform)
		else: vtype = forced_inflection_vtype
		if vtype == voikkoutils.VOWEL_FRONT: vfst_vtype = u'ä'
		elif vtype == voikkoutils.VOWEL_BACK: vfst_vtype = u'a'
		elif vtype == voikkoutils.VOWEL_BOTH: vfst_vtype = u'aä'
		vocabularyFile = vocabularyFiles[vfst_word_class.replace(u"[L", u"").replace(u"]", u"")]
		if alku == None:
			errorstr = u"ERROR: Malaga class not found for (%s, %s)\n" \
				% (wordform, voikko_infclass)
			generate_lex_common.write_entry(vocabularyFile, {}, word, errorstr)
			sys.stderr.write(errorstr.encode(u"UTF-8"))
			sys.exit(1)
		alku = alku.lower()
		(rakenne, alkuWithTags) = get_structure(altform, vfst_word_class, alku)
		
		if vfst_word_class == u"[Lh]":
			entry = u'%s[Xp]%s[X]%s%s:%s # ;' % (vfst_word_class, wordform, rakenne, alkuWithTags, alku)
			vocabularyFile.write(entry + u"\n")
			continue
		vfst_class_prefix = get_vfst_class_prefix(vfst_word_class)
		
		# Vowel type in derived verbs
		if jatko in [u"Heittää", u"Muistaa", u"Juontaa", u"Hohtaa", u"Murtaa", u"Nousta", u"Loistaa", u"Jättää", u"Kihistä"]:
			diacritics = diacritics + vowel_type_for_derived_verb(alkuWithTags)
			if jatko == u"Kihistä" and vtype == voikkoutils.VOWEL_FRONT and u"y" not in alku and u"ä" not in alku and u"ö" not in alku and u"e" in alku:
				jatko = u"Helistä"
		
		if jatko == u"Nainen" and vfst_class_prefix in [u"Laatusana", u"NimiLaatusana"] and altform.endswith(u"inen"):
			jatko = u"NainenInen"
		
		if vfst_word_class == u"[Lp]":
			entry = u'[Lp]%s%s%s%s:%s%s EtuliitteenJatko_%s;' \
			        % (rakenne, alkuWithTags, diacritics, infoFlags, alku, diacritics, get_prefix_jatko(word, altform))
		else:
			entry = u'%s[Xp]%s[X]%s%s%s%s%s:%s%s %s%s_%s ;' \
			        % (vfst_word_class, wordform, debug_info, rakenne, infoFlags,
			        alkuWithTags, diacritics, alku, diacritics, vfst_class_prefix, jatko, vfst_vtype)
		vocabularyFile.write(entry + u"\n")
	
	# Sanity check for alternative forms: if there are both multi part forms and single part forms
	# then all multi part forms must end with a part contained in the single part set.
	if singlePartForms:
		for multiPartForm in multiPartForms:
			lastPart = multiPartForm[max(rfind(multiPartForm, u"="), rfind(multiPartForm, u"|"), rfind(multiPartForm, u"-")) + 1:]
			if lastPart not in singlePartForms:
				sys.stderr.write(u"ERROR: suspicious alternative spelling: %s\n" % multiPartForm)
				sys.exit(1)


voikkoutils.process_wordlist(generate_lex_common.VOCABULARY_DATA + u'/joukahainen.xml', \
                             handle_word, True)

for fileSuffix in vocabularyFileSuffixes:
	vocabularyFiles[fileSuffix].write(u"\n\n") # Extra line feeds needed to avoid mixed lines in concatenated lexc file
	vocabularyFiles[fileSuffix].close()
