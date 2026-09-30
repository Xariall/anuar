# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Not a code repository. There is no build, lint, or test tooling, no git history, and no README. The directory holds a collection of contract templates (Word/Excel) in Russian/Kazakh that regional akimat bodies (МИО) use for the "Ауыл-Аманат" agricultural lending program. Work here is reading, comparing, and editing documents.

## Layout

Everything lives under `шаблоны МИО/`, one folder per region, numbered 1–17 in alphabetical order of the region name (Акмолинская, Актюбинская, Алматинская, … Туркестанская). Each region folder has a `договора/` subfolder with that region's templates. Exceptions:

- `17. Туркестанская область/` uses the misspelling `договара/` and also has loose copies of the same three `.doc` files at the region root.
- `14. Область Ұлытау/` contains only two files, a loan and a pledge agreement for one specific КХ.

Regions are not uniform. Each has its own set and naming, typically a subset of:

- loan or credit agreements (займа, кредита), sometimes split by borrower type: ИП, СПК, физ. лиц
- pledge agreements (залога), sometimes split into movable, immovable, future property, or three-party
- guarantee agreements (гарантии), sometimes split by individual or legal entity
- leasing sets (Костанай, ЗКО, Туркестан) with sale-purchase (ДКП) and supplier agreements
- agency agreements (договор поручения, Мангистау and Кызылорда) in Russian and Kazakh versions, with numbered appendices (`Приложение 2–10`, and an `.xlsx` for 6–9)

## Working with these files

- Mixed formats: legacy `.doc` and `.docx`, plus one `.xlsx`. Filenames contain Cyrillic and spaces, so always quote paths.
- Some files are filled-in examples for a named borrower rather than blank templates (e.g. `ДЗ Балмұқан…` in Ұлытау, `залог №2026-СПК-АА-2 СПК Сейтжапар` in Караганда, `Договор залога ИП Касымов 1` in Павлодар). Check for borrower names, dates, and amounts before treating a file as a generic template.
- Names like `(1)`, `++25.09.26++` and `новый шаблон` mark duplicate or versioned copies. Compare against sibling files before deciding which is current.
- Cross-region questions ("how does each region handle guarantees?") require opening the documents individually. Nothing indexes or normalizes them.
- Preserve the original formatting when editing Word files, and don't convert `.doc` to `.docx` unless asked.
