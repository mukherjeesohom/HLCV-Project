import torch
import torch.optim as optim
import torch.nn as nn
import argparse
import os
import matplotlib.pyplot as plt

from datasets.dataset_read import dataset_read
from model.build_gen import CustLeNet

# loader = torch.utils.data.DataLoader(data, batch_size=500)

def get_accuracy(model, dataloader):

    correct, total = 0, 0
    for xs, ts in dataloader:
        # xs = xs.view(-1, 784) # flatten the image
        ts = ts.cuda()
        zs = model(xs.cuda())
        pred = zs.max(1, keepdim=True)[1] # get the index of the max logit
        correct += pred.eq(ts.view_as(pred)).sum().item()
        total += int(ts.shape[0])

    return correct / total


if __name__ == '__main__':

    # Training settings
    parser = argparse.ArgumentParser(description='Pretraining')
    parser.add_argument('--all_use', type=str, default='no', metavar='N',
                        help='use all training data? in usps adaptation')
    parser.add_argument('--batch-size', type=int, default=128, metavar='N',
                        help='input batch size for training (default: 64)')
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoint', metavar='N',
                        help='source only or not')
    # parser.add_argument('--eval_only', action='store_true', default=False,
                        # help='evaluation only option')
    parser.add_argument('--lr', type=float, default=0.0002, metavar='LR',
                        help='learning rate (default: 0.0002)')
    parser.add_argument('--load_epoch', type=int, default=0, metavar='N',
                        help='at which epoch of training model to load')
    parser.add_argument('--no-cuda', action='store_true', default=False,
                        help='disables CUDA training')
    # parser.add_argument('--num_k', type=int, default=4, metavar='N',
                        # help='hyper paremeter for generator update')
    # parser.add_argument('--one_step', action='store_true', default=False,
                        # help='one step training with gradient reversal layer')
    # parser.add_argument('--optimizer', type=str, default='adam', metavar='N', help='which optimizer')
    # parser.add_argument('--resume_epoch', type=int, default=100, metavar='N',
                        # help='epoch to resume')
    parser.add_argument('--save_epoch', type=int, default=10, metavar='N',
                        help='when to restore the model')
    parser.add_argument('--save_model', action='store_true', default=False,
                        help='save_model or not')
    parser.add_argument('--seed', type=int, default=1, metavar='S',
                        help='random seed (default: 1)')
    parser.add_argument('--source', type=str, default='svhn', metavar='N',
                        help='source dataset')
    parser.add_argument('--target', type=str, default='mnist', metavar='N', help='target dataset')
    # parser.add_argument('--use_abs_diff', action='store_true', default=False,
                        # help='use absolute difference value as a measurement')
 
    args = parser.parse_args()
    args.cuda = not args.no_cuda and torch.cuda.is_available()
    torch.manual_seed(args.seed)
 
    if args.cuda:
        torch.cuda.manual_seed(args.seed)
 
    print(args)

    batch_size = args.batch_size
    source = args.source
    # source = 'mnist'
    target = args.target
    # num_k = args.num_k
    checkpoint_dir = args.checkpoint_dir
    save_epoch = args.save_epoch
    # use_abs_diff = args.use_abs_diff
    all_use = args.all_use
    print_interval = 100

    if source == 'svhn':
        scale = True
    else:
        scale = False

    # optimizer = args.optimizer
    # LR = args.lr
    
    if not os.path.exists(args.checkpoint_dir):
        os.mkdir(args.checkpoint_dir)

    print('dataset loading')
    train_loader, val_loader = dataset_read(target, source, batch_size, scale, all_use) # changed the loaded data to target
    print('load finished!')

    device = torch.device("cuda")

    model = CustLeNet(source, target).cuda()

    optimizer = optim.Adam(model.parameters(), lr = args.lr, weight_decay=0.0001)

    criterion = nn.CrossEntropyLoss().cuda()

    torch.cuda.manual_seed(1) # fixing seed according to MCD work

    #
    model.load_state_dict(torch.load(f'{args.checkpoint_dir}/{source+target}_epoch_{args.load_epoch}.pth'))

    accuracy = get_accuracy(model.cuda(), train_loader)

    print(f"Accuracy (on {target})= {accuracy}")