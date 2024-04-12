import brand_config
from brand_os import BrandOS

def main():
    config = brand_config.load_config()
    brand_os = BrandOS(config)
    brand_os.run()

if __name__ == "__main__":
    main()