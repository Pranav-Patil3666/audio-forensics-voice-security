from __future__ import annotations

import torch


def get_device(
    prefer_cuda: bool = True,
) -> torch.device:

    if prefer_cuda and torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def device_name(device: torch.device) -> str:
    if device.type == "cuda":
        return torch.cuda.get_device_name(device)

    return "CPU"


def move_to_device(
    tensor_or_model,
    device: torch.device,
):

    return tensor_or_model.to(device)


def clear_cuda_cache() -> None:
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def inference_mode():
    return torch.inference_mode()