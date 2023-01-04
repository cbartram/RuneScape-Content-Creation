# RuneScape YouTube Suggestions

This application uses a clustering algorithm to identify and tag reddit topics in 2007Scape. Through the YouTube API it 
then creates a score for each category based on how much content has been created for the related category. Finally, 
the application will use the score to suggest which RuneScape content to create based on a high number of reddit
posts with a low YouTube score.

## Getting Started

To get started with this system simply clone this repository and run the main file using: 

```shell
python -m main
```

### Prerequisites

This application requires python >= 3.10 to be installed and running on your system.
- [Python](https://www.python.com)

Note: Lower versions of Python may work but have not been tested. Use at your own risk.

## Running the tests

Tests are managed through PyTest and can be run with: 

```shell
pytest -s -vv
```

### Style test

Checks if the best practices and the right coding style has been used. This is managed through Black and can be run with:

    black

## Deployment

Depoloyment coming soon.

## Built With

  - [Python3](https://www.python.org) - Programming Language used

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code
of conduct, and the process for submitting pull requests to us.

## Versioning

We use [Semantic Versioning](http://semver.org/) for versioning. For the versions
available, see the [tags on this
repository](https://github.com/cbartram/RuneScape-Content-Creation/tags).

## Authors

  - **Christian Bartram** - Developer - [cbartram](https://github.com/cbartram)

## License

This project is licensed under the [CC0 1.0 Universal](LICENSE.md)
Creative Commons License - see the [LICENSE.md](LICENSE.md) file for
details

