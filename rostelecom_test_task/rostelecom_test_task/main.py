from HTMLParserRialcom import HTMLParserRialcom


def main():
    data_parser = HTMLParserRialcom()

    result = data_parser.load_data()
    if result == 200:
        data_parser.save_data()

    else:
        print(f"Status Code: {result}")


if __name__ == "__main__":
    main()
