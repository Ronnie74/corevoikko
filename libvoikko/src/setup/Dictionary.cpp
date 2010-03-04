/* Libvoikko: Library of Finnish language tools
 * Copyright (C) 2008 - 2010 Harri Pitkänen <hatapitk@iki.fi>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 *********************************************************************************/

#include "setup/Dictionary.hpp"

using namespace std;

namespace libvoikko { namespace setup {

Dictionary::Dictionary() :
	morPath(),
	morBackend(),
	spellBackend(),
	suggestionBackend(),
	variant(),
	description(),
	isDefaultDict(false) {
}

Dictionary::Dictionary(const string & morPath, const string & morBackend,
                       const string & spellBackend,
                       const string & suggestionBackend,
                       const string & variant,
                       const string & description) :
	morPath(morPath),
	morBackend(morBackend),
	spellBackend(spellBackend),
	suggestionBackend(suggestionBackend),
	variant(variant),
	description(description),
	isDefaultDict(false) {
}

Dictionary::Dictionary(const Dictionary & dictionary) :
	morPath(dictionary.morPath),
	morBackend(dictionary.morBackend),
	spellBackend(dictionary.spellBackend),
	suggestionBackend(dictionary.suggestionBackend),
	variant(dictionary.variant),
	description(dictionary.description),
	isDefaultDict(dictionary.isDefaultDict) {
}

const string & Dictionary::getMorPath() const {
	return morPath;
}

const string & Dictionary::getMorBackend() const {
	return morBackend;
}

const string & Dictionary::getSpellBackend() const {
	return spellBackend;
}

const string & Dictionary::getSuggestionBackend() const {
	return suggestionBackend;
}

const string & Dictionary::getVariant() const {
	return variant;
}

const string & Dictionary::getDescription() const {
	return description;
}

bool Dictionary::isValid() const {
	return !variant.empty();
}

bool Dictionary::isDefault() const {
	return isDefaultDict;
}

void Dictionary::setDefault(bool isDefault) {
	this->isDefaultDict = isDefault;
}

bool operator<(const Dictionary & d1, const Dictionary & d2) {
	return d1.variant < d2.variant;
}

} }
