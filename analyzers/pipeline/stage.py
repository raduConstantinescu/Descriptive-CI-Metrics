
# Base class for all pipeline stages
class PipelineStage:
    def run(self):
        raise NotImplementedError()