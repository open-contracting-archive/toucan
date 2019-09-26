To regenerate the result fixtures:

    cat tests/fixtures/1.1/release-packages/0001-tender.json tests/fixtures/1.1/release-packages/0001-award.json tests/fixtures/1.1/release-packages/0002-tender.json | ocdskit compile --package > tests/fixtures/results/compile.json
    cat tests/fixtures/1.0/release-packages/0001-tender.json | ocdskit upgrade 1.0:1.1 > tests/fixtures/results/upgrade.json
    cat tests/fixtures/1.1/releases/0001-tender.json tests/fixtures/1.1/releases/0001-award.json tests/fixtures/1.1/releases/0002-tender.json | ocdskit package-releases > tests/fixtures/results/package-releases.json
