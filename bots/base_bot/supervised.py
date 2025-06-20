from dataset import MahjongGBDataset, AugmentedMahjongGBDataset
from torch.utils.data import DataLoader
from model import CNNModel, MahjongModel, ResMahjongModel
import torch.nn.functional as F
import torch
import os
from custom_losses import FocalLoss, LabelSmoothingLoss
from torch.optim.lr_scheduler import _LRScheduler
import math
import argparse

class WarmupCosineScheduler(_LRScheduler):
    def __init__(self, optimizer, warmup_epochs, max_epochs, warmup_start_lr=1e-8, eta_min=1e-8, last_epoch=-1):
        self.warmup_epochs = warmup_epochs
        self.max_epochs = max_epochs
        self.warmup_start_lr = warmup_start_lr
        self.eta_min = eta_min
        super(WarmupCosineScheduler, self).__init__(optimizer, last_epoch)

    def get_lr(self):
        if self.last_epoch < self.warmup_epochs:
            return [self.warmup_start_lr + (base_lr - self.warmup_start_lr) * (self.last_epoch / self.warmup_epochs)
                    for base_lr in self.base_lrs]
        else:
            return [self.eta_min + (base_lr - self.eta_min) *
                    (1 + math.cos(math.pi * (self.last_epoch - self.warmup_epochs) / (self.max_epochs - self.warmup_epochs))) / 2
                    for base_lr in self.base_lrs]


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Train Mahjong model')
    # parser.add_argument('--resume', type=str, help='path to checkpoint to resume from')
    # parser.add_argument('--start_epoch', type=int, default=0, help='epoch to start training from')
    # args = parser.parse_args()

    logdir = 'model/'
    os.makedirs(logdir + 'checkpoint', exist_ok=True)
    
    # Load dataset
    splitRatio = 0.9
    batchSize = 8192
    originalDataset = MahjongGBDataset(0, splitRatio, True)
    trainDataset = AugmentedMahjongGBDataset(originalDataset, augmentation_factor=1)
    validateDataset = MahjongGBDataset(splitRatio, 1, False)
    loader = DataLoader(dataset = trainDataset, batch_size = batchSize, shuffle = True)
    vloader = DataLoader(dataset = validateDataset, batch_size = batchSize, shuffle = False)
    
    # Load model
    ## model = CNNModel().to('cuda')
    # model = MahjongModel().to('cuda')
    model = ResMahjongModel().to('cuda')
    optimizer = torch.optim.Adam(model.parameters(), lr = 0.01)
    # optimizer = torch.optim.SGD(model.parameters(), lr = 0.4)
    scheduler = WarmupCosineScheduler(optimizer, max_epochs=96, warmup_epochs=5, warmup_start_lr=1e-6)
    loss_fn = F.cross_entropy
    # loss_fn = FocalLoss()
    # loss_fn = LabelSmoothingLoss(235)
    
    # Load checkpoint if resuming
    # if args.resume:
    #     if os.path.isfile(args.resume):
    #         print(f"Loading checkpoint '{args.resume}'")
    #         checkpoint = torch.load(args.resume)
    #         args.start_epoch = checkpoint['epoch']
    #         model.load_state_dict(checkpoint['state_dict'])
    #         optimizer.load_state_dict(checkpoint['optimizer'])
    #         scheduler.load_state_dict(checkpoint['scheduler'])
    #         print(f"Loaded checkpoint '{args.resume}' (epoch {checkpoint['epoch']})")
    #     else:
    #         print(f"No checkpoint found at '{args.resume}'")
    
    # Train and validate
    for e in range(96):
        print('Epoch', e)
        torch.save(model.state_dict(), logdir + 'checkpoint/%d.pkl' % e)
        _correct = 0
        for i, d in enumerate(loader):
            input_dict = {'is_training': True, 'obs': {'observation': d[0].cuda(), 'action_mask': d[1].cuda()}}
            logits = model(input_dict)
            pred = logits.argmax(dim = 1)
            _correct += torch.eq(pred, d[2].cuda()).sum().item()
            loss = loss_fn(logits, d[2].long().cuda())
            if i % 128 == 0:
                print('Iteration %d/%d'%(i, len(trainDataset) // batchSize + 1), 'policy_loss', loss.item())
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print('Epoch', e + 1, 'Train acc:', _correct / len(trainDataset))
        print('Run validation:')
        correct = 0
        for i, d in enumerate(vloader):
            input_dict = {'is_training': False, 'obs': {'observation': d[0].cuda(), 'action_mask': d[1].cuda()}}
            with torch.no_grad():
                logits = model(input_dict)
                pred = logits.argmax(dim = 1)
                correct += torch.eq(pred, d[2].cuda()).sum().item()
        acc = correct / len(validateDataset)
        print('Epoch', e + 1, 'Validate acc:', acc)
        scheduler.step()
        with open('val_acc.txt', 'a') as f:
            f.write(f'Epoch {e+1}, Validate acc: {acc}\n')