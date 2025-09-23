class Dotclaude < Formula
  include Language::Python::Virtualenv

  desc "Sync Claude Code configurations between local and remote repositories"
  homepage "https://github.com/FradSer/dotclaude-cli"
  url "https://github.com/FradSer/dotclaude-cli/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "f2ee82a3c4686a705758e976e1dd8b1ade828f9304291726dd7526f3420f7a02"
  version "0.1.0"
  license "MIT"

  depends_on "python@3.12"
  depends_on "git"

  resource "typer" do
    url "https://files.pythonhosted.org/packages/source/t/typer/typer-0.18.0.tar.gz"
    sha256 "3cb76b446e5ce3b1ac1f55d26ce7c7db1c7a19e7b07f12fd48fcfcebc7bc60e0"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.7.1.tar.gz"
    sha256 "9be308cb1fe2f1f57d67ce99e95af38a1e2bc71ad9813b0e247cf7ffbcc3a432"
  end

  resource "GitPython" do
    url "https://files.pythonhosted.org/packages/source/G/GitPython/GitPython-3.1.43.tar.gz"
    sha256 "35f314a9f878467f5453cc1fee295c3e18e52f1b99f10f6cf5b1682e968a9e7c"
  end

  resource "ruamel.yaml" do
    url "https://files.pythonhosted.org/packages/source/r/ruamel.yaml/ruamel.yaml-0.18.6.tar.gz"
    sha256 "8b27e6a217e786c6fbe5634d8f3f11bc63e0f80f6a5890f28863d9c45aac311b"
  end

  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/source/p/pydantic/pydantic-2.5.3.tar.gz"
    sha256 "b3ef57c62535b0941697cce638c08900d87fcb67e29cfa99e8a68f747f393f7a"
  end

  resource "aiofiles" do
    url "https://files.pythonhosted.org/packages/source/a/aiofiles/aiofiles-23.2.1.tar.gz"
    sha256 "84ec2218d8419404abcb9f0c02df3f34c6e0a68ed41072acfb1cef5cbc29051a"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/source/c/click/click-8.1.7.tar.gz"
    sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
  end

  resource "inquirer" do
    url "https://files.pythonhosted.org/packages/source/i/inquirer/inquirer-3.2.4.tar.gz"
    sha256 "8edc99c076386ee2d2204e5e3653c2488244de26976e880f90161fcb2ebebde8"
  end

  # Additional dependencies for the resources above
  resource "typing-extensions" do
    url "https://files.pythonhosted.org/packages/source/t/typing-extensions/typing_extensions-4.9.0.tar.gz"
    sha256 "23478f88c37f27d76ac8aee6c905017a143b0b1b886c3c9f66bc2fd94f9f5783"
  end

  resource "annotated-types" do
    url "https://files.pythonhosted.org/packages/source/a/annotated-types/annotated_types-0.6.0.tar.gz"
    sha256 "563339e807e53ffd9c267e99fc6d9ea23eb8443c08f112651963e24e22f84a5d"
  end

  resource "pydantic-core" do
    url "https://files.pythonhosted.org/packages/source/p/pydantic-core/pydantic_core-2.14.6.tar.gz"
    sha256 "1fd0c1d395372843fba13a51c28e3bb9d59bd7aebfeb17358ffaaa1e4dbbe948"
  end

  resource "gitdb" do
    url "https://files.pythonhosted.org/packages/source/g/gitdb/gitdb-4.0.11.tar.gz"
    sha256 "bf5421126136d6d0af55bc1e7c1af1c397a34f5b7bd79e776cd3e89785c2b04b"
  end

  resource "smmap" do
    url "https://files.pythonhosted.org/packages/source/s/smmap/smmap-5.0.1.tar.gz"
    sha256 "dceeb6c0028fdb6734471eb07c0cd2aae706ccaecab45965ee83f11c8d3b1f62"
  end

  resource "ruamel.yaml.clib" do
    url "https://files.pythonhosted.org/packages/source/r/ruamel.yaml.clib/ruamel.yaml.clib-0.2.8.tar.gz"
    sha256 "beb2e0404003de9a4cab9753a8805a8fe9320ee6673136ed7f04255fe60bb512"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/source/m/markdown-it-py/markdown_it_py-3.0.0.tar.gz"
    sha256 "e3f60a94fa066dc52ec76661e37c851cb232d92f9886b15cb560aaada2df8feb"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/source/m/mdurl/mdurl-0.1.2.tar.gz"
    sha256 "bb413d29f5eea38f31dd4754dd7377d4465116fb207585f97bf925588687c1ba"
  end

  resource "pygments" do
    url "https://files.pythonhosted.org/packages/source/p/pygments/Pygments-2.17.2.tar.gz"
    sha256 "da46cec9fd2de5be3a8a784f434e4c4ab670b4ff54d605c4c2717e9d49c4c367"
  end

  resource "blessed" do
    url "https://files.pythonhosted.org/packages/source/b/blessed/blessed-1.20.0.tar.gz"
    sha256 "2cdd67f8746e048f00df47a2880f4d6acbcdb399031b604e34ba8f71d5787680"
  end

  resource "editor" do
    url "https://files.pythonhosted.org/packages/source/e/editor/editor-1.6.6.tar.gz"
    sha256 "bb6989e872638cd119db9a4fce284cd8e13c553886a1c044c6b8d8a160c871f8"
  end

  resource "python-editor" do
    url "https://files.pythonhosted.org/packages/source/p/python-editor/python_editor-1.0.4.tar.gz"
    sha256 "51fda6bcc5ddbbb7063b2af7509e43bd84bfc32a4ff71349ec7847713882327b"
  end

  resource "readchar" do
    url "https://files.pythonhosted.org/packages/source/r/readchar/readchar-4.0.5.tar.gz"
    sha256 "08a456c2d7c1888cde3f4688b542621b676eb38cd6cfed7eb0fb24c7a93995da"
  end

  resource "wcwidth" do
    url "https://files.pythonhosted.org/packages/source/w/wcwidth/wcwidth-0.2.12.tar.gz"
    sha256 "f01c104efdf57971bcb756f054dd58ddec5204dd15fa31d6503ea57947d97c02"
  end

  resource "six" do
    url "https://files.pythonhosted.org/packages/source/s/six/six-1.16.0.tar.gz"
    sha256 "1e61c37477a1626458e36f7b1d82aa5c9b094fa4802892072e49de9c60c4c926"
  end

  def install
    virtualenv_install_with_resources

    # Generate shell completions
    generate_completions_from_executable(bin/"dotclaude", shells: [:bash, :zsh, :fish], shell_parameter_format: :click)
  end

  test do
    # Test basic functionality
    assert_match "dotclaude", shell_output("#{bin}/dotclaude --help")

    # Test version
    version_output = shell_output("#{bin}/dotclaude --version")
    assert_match version.to_s, version_output

    # Test status command (should work without git repo)
    status_output = shell_output("#{bin}/dotclaude status", 1)  # Expected to fail gracefully
    assert_match(/error|status/, status_output.downcase)
  end
end