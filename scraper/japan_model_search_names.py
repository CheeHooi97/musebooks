"""Build specific name variants for Japan-market model searches."""
import re
import unicodedata


def _key(value):
    return "".join(
        character for character in unicodedata.normalize("NFKC", value).casefold()
        if character.isalnum()
    )


def physical_model_search_names(person):
    """Keep full catalog names and useful full aliases; skip partial aliases.

    A short alias contained in a catalog name is usually a given-name fragment
    rather than a safe marketplace identity. Full alternate names remain useful
    search terms.
    """
    primary = [person.get(key) for key in (
        "original_name", "canonical_public_name", "english_name"
    )]
    names = []
    seen = set()
    for value in primary:
        value = (value or "").strip()
        key = _key(value)
        if value and key and key not in seen:
            names.append(value)
            seen.add(key)

    primary_keys = [_key(value) for value in names]
    for value in person.get("aliases", []):
        value = (value or "").strip()
        key = _key(value)
        if not value or not key or key in seen:
            continue
        if any(key in primary_key and len(key) < len(primary_key)
               for primary_key in primary_keys):
            continue

        latin_tokens = re.findall(r"[A-Za-z0-9]+", value)
        looks_like_full_latin_name = len(latin_tokens) >= 2
        looks_like_full_native_name = len(key) >= 3
        if not (looks_like_full_latin_name or looks_like_full_native_name):
            continue

        names.append(value)
        seen.add(key)
    return names


def model_name_matches_identity_field(names, field):
    """Match a source person-name field by full name, never by substring."""
    separators = re.compile(r"[,，、/／|｜;；&＆·・()（）\[\]{}【】「」『』<>\n\r]+")
    field_keys = {_key(field)}
    field_keys.update(_key(part) for part in separators.split(field or ""))
    field_keys.discard("")
    return any(key in field_keys for name in names if (key := _key(name)))
