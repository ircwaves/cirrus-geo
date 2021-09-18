import logging
import click

from typing import List
from pathlib import Path

from .. import files
from .component import Component
from cirrus.cli.utils.yaml import NamedYamlable


logger = logging.getLogger(__name__)


class Lambda(Component):
    handler = files.PythonHandler()
    definition = files.LambdaDefinition()
    # TODO: Readme should be required once we have one per task
    readme = files.Readme(optional=True)

    def load_config(self):
        self.config = NamedYamlable.from_yaml(self.definition.content)
        self.description = self.config.get('description', '')
        self.enabled = self.config.get('enabled', True)
        self.python_requirements = self.config.pop('python_requirements', [])

        self.lambda_config = self.config.get('lambda', NamedYamlable())
        self.lambda_enabled = self.lambda_config.pop('enabled', True) and self.enabled
        self.lambda_config.description = self.description
        self.lambda_config.environment = self.config.get('environment', {})

        if not hasattr(self.lambda_config, 'module'):
            self.lambda_config.module = f'lambdas/{self.name}'
        if not hasattr(self.lambda_config, 'handler'):
            self.lambda_config.handler = 'handler.handler'

    @click.command()
    def show(self):
        click.echo(self.files)

    def get_outdir(self, project_build_dir: Path) -> Path:
        return project_build_dir.joinpath(self.lambda_config.module)

    def link_to_outdir(self, outdir: Path, project_python_requirements: List[str]) -> None:
        try:
            outdir.mkdir(parents=True)
        except FileExistsError:
            self.clean_outdir(outdir)

        for _file in self.path.iterdir():
            if _file.name == self.definition.name:
                logger.debug('Skipping linking definition file')
                continue
            # TODO: could have a problem on windows
            # if lambda has a directory in it
            # probably affects handler default too
            outdir.joinpath(_file.name).symlink_to(_file)

        reqs = self.python_requirements + project_python_requirements
        outdir.joinpath('requirements.txt').write_text(
            '\n'.join(reqs),
        )

    def clean_outdir(self, outdir: Path):
        try:
            contents = outdir.iterdir()
        except FileNotFoundError:
            return

        for _file in contents:
            _file.unlink()
