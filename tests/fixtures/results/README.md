To regenerate the result fixtures:

    flatten-tool flatten --main-sheet-name releases --root-id ocid --root-list-path releases --remove-empty-schema-columns tests/fixtures/1.1/release-packages/0001-tender.json -o tests/fixtures/results/flattened

    cat tests/fixtures/1.1/release-packages/0001-tender.json tests/fixtures/1.1/release-packages/0001-award.json tests/fixtures/1.1/release-packages/0002-tender.json | ocdskit compile --package > tests/fixtures/results/compile.json
    cat tests/fixtures/1.1/release-packages/0001-tender.json tests/fixtures/1.1/release-packages/0001-award.json tests/fixtures/1.1/release-packages/0002-tender.json | ocdskit compile --package --published-date 2001-02-03T00:00:00Z > tests/fixtures/results/compile-published-date.json
    cat tests/fixtures/1.1/release-packages/0001-tender.json tests/fixtures/1.1/release-packages/0001-award.json tests/fixtures/1.1/release-packages/0002-tender.json | ocdskit compile --package --versioned > tests/fixtures/results/compile-versioned.json

    cat tests/fixtures/1.1/releases/0001-tender.json tests/fixtures/1.1/releases/0001-award.json tests/fixtures/1.1/releases/0002-tender.json | ocdskit package-releases > tests/fixtures/results/package-releases.json
    cat tests/fixtures/1.1/releases/0001-tender.json tests/fixtures/1.1/releases/0001-award.json tests/fixtures/1.1/releases/0002-tender.json | ocdskit package-releases --published-date 2001-02-03T00:00:00Z > tests/fixtures/results/package-releases_published-date.json

    cat tests/fixtures/1.0/release-packages/0001-tender.json | ocdskit upgrade 1.0:1.1 > tests/fixtures/results/upgrade.json

    curl -O https://standard.open-contracting.org/latest/en/release-schema.json
    ocdskit mapping-sheet --infer-required release-schema.json > tests/fixtures/results/mapping-sheet.csv
    rm -f release-schema.json
