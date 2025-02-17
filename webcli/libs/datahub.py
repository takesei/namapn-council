from dataclasses import dataclass, field
import pandas as pd
import yaml
from importlib import resources
from libs.store import DataCatalog


@dataclass
class DataContent:
    name: str
    keys: list[str]
    values: list[str]
    segments: list[str]

    df: pd.DataFrame
    versions: list[str] | None = field(init=False)

    def __post_init__(self) -> None:
        if "version" in self.df.columns:
            self.versions = self.df.version.unique().tolist()
        else:
            self.versions = None

    def diff(
        self,
        target_versions: str | list[str],
        segments: str | list[str] | None = None,
        values: str | list[str] | None = None,
    ) -> pd.DataFrame:
        if segments is None:
            segments = []
        if values is None:
            values = self.values



        if self.versions is None:
            raise ValueError(
                f"Table {self.name} does not support diff method, since it does not have version attr."
            )
        tversion = (
            [target_versions] if isinstance(target_versions, str) else target_versions
        )
        for tversion in target_versions:
            if tversion not in self.versions:
                raise KeyError(f"target version {tversion} not found")
        segments = [segments] if isinstance(segments, str) else segments
        for segment in segments:
            if segment not in self.segments:
                raise KeyError(f"segment {segment} not found")
        values = [values] if isinstance(values, str) else values
        for value in values:
            if value not in self.values:
                raise KeyError(f"value {value} not found")

        df = (
            self.df.loc[
                self.df.version.isin(target_versions),
                [*self.keys, *segments, *values],
            ]
            .groupby([*self.keys, *segments])
            .sum()
            .loc[:, values]
            .reset_index()
        )

        temp = None

        for version in target_versions:
            df_temp = df[df.version == version]
            df_temp = df_temp.rename(
                columns={value: f"{value}_{version}" for value in values}
            )
            df_temp = df_temp.drop(columns=["version"])

            if temp is None:
                temp = df_temp
            else:
                k = [*self.keys, *segments]
                k.remove("version")
                try:
                    temp = pd.merge(
                        temp,
                        df_temp,
                        left_on=k,
                        right_on=k,
                        how="outer",
                    )
                except Exception as e:
                    print("Error occured during merge")
                    print(temp)
                    print(df_temp)
                    raise e
        temp["label"] = ""
        for _, col in temp.loc[:, segments].items():
            temp.label += col
        return temp.sort_values("time_id")


class DataHub:
    versions: list[str]
    _contents: dict[str, DataContent]

    def contents(self) -> list[str]:
        return list(self._contents.keys())

    def __getitem__(self, key: str):
        return self._contents[key]

    def items(self):
        return self._contents.items()

    def __init__(self, db: DataCatalog) -> None:
        cont = {}
        versions = set()

        file_path = resources.files("libs.tables").joinpath("datahub.yml")
        with file_path.open("r", encoding="utf-8") as f:
            tables = yaml.safe_load(f)

        for table in tables:
            df = db.get(table["name"])
            df.time_id = pd.to_datetime(df.time_id)
            versions |= set(df.version)
            cont |= {
                table["name"]: DataContent(
                    name=table["name"],
                    keys=table["keys"],
                    values=table["values"],
                    segments=table["segments"],
                    df=df,
                )
            }
        self._contents = cont
        self.versions = versions
