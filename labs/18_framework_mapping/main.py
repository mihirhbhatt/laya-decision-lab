from laya_labs.grc.frameworks import FrameworkMapping


def main():
    mapping = FrameworkMapping(
        source_framework="NIST", source_control="SC-13",
        target_framework="ISO27001", target_control="A.8.24",
        mapping_type="RELATED", rationale="Both address cryptographic protection.",
    )
    print(mapping)


if __name__ == "__main__":
    main()