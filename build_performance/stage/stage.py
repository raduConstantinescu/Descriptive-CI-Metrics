
# Base class for all pipeline stages
class PipelineStage:
    def run(self):
        raise NotImplementedError()

    def log_info(self, message):
        if self.verbose:
            print(message)