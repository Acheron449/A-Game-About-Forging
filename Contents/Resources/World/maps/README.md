# TMX [![Continuous Integration](https://github.com/kreemer/tmx/actions/workflows/continuous-integration.yaml/badge.svg?branch=main)]

[![Total Downloads](https://img.shields.io/packagist/dt/kreemer/tmx.svg)](https://packagist.org/packages/kreemer/tmx)
[![Latest Stable Version](https://img.shields.io/packagist/v/kreemer/tmx.svg)](https://packagist.org/packages/kreemer/tmx)
[![Code Coverage](https://img.shields.io/codecov/c/github/kreemer/tmx)](https://app.codecov.io/gh/kreemer/tmx)

TMX is a library for creating, parsing and editing tmx files. The main purpose is to parse a tmx file and save the
parsed file as image file.

The tmx format is used by the program [Tiled](https://www.mapeditor.org). The format is
explained [here](https://doc.mapeditor.org/en/stable/reference/tmx-map-format/).

## Installation

Install the latest version with

```bash
$ composer require kreemer/tmx
```

## Basic Usage

```php
<?php

use Tmx\Service\Parser;
use Tmx\Service\Printer;

$parser = new Parser();
$map = $parser->parse('filename.tmx');

echo $map->getWidth(); // get width of map
echo $map->getHeight(); // get height of map

$printer = new Printer();
$printer->print($map, 'output.png'); // save map to output.png
```

## Documentation

See [here](https://kreemer.github.io/tmx) for additional documentation.

## About

### Requirements

- Tmx works with PHP 7.4 or above.
- You have to install the imagick extension, gd support is currently under development
- If you want to parse zlib or zstd compressed maps, you have to install these extensions

### Submitting bugs and feature requests

Bugs and feature request are tracked on [GitHub](https://github.com/kreemer/tmx/issues)

### Attribution

This library uses [Serene village revamped](https://limezu.itch.io/serenevillagerevamped) tiles for automatic tests. The tileset is under the [Creative commons](https://creativecommons.org/licenses/by/4.0/) license.

Please support the original developer for this wonderful tileset.

### License

Tmx is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

