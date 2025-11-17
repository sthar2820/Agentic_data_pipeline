def __init__(self, config: Dict[str, Any], artifacts_path: str):
    self.config = config
    self.artifacts_path = artifacts_path
    self.logger = logging.getLogger(self.__class__.__name__)
    os.makedirs(self.artifacts_path, exist_ok=True)
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
