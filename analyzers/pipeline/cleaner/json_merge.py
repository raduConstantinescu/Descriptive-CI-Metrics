import json

from analyzers.pipeline.stage import PipelineStage


class JsonMergeConfig:
    def __init__(self, config):
        self.input_files = config["input_files"]
        self.output_file = config["output_file"]


class JsonMergeStage(PipelineStage):
    def __init__(self, args, config: JsonMergeConfig):
        self.verbose = args.verbose
        self.config = config

    def run(self):
        merged_data = {}
        for input_file in self.config.input_files:
            with open(input_file) as f:
                data = json.load(f)
                merged_data.update(data)
        with open(self.config.output_file, 'w') as f:
            json.dump(merged_data, f, indent=4)

        if self.verbose:
            print(f"Merged {len(self.config.input_files)} JSON files into {self.config.output_file}")
