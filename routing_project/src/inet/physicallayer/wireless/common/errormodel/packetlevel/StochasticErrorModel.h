//
// Copyright (C) 2013 OpenSim Ltd.
//
// SPDX-License-Identifier: LGPL-3.0-or-later
//


#ifndef __INET_STOCHASTICERRORMODEL_H
#define __INET_STOCHASTICERRORMODEL_H

#include "inet/physicallayer/wireless/common/base/packetlevel/ErrorModelBase.h"

namespace inet {

namespace physicallayer {

/**
 * Implements the StochasticErrorModel model, see the NED file for details.
 */
class INET_API StochasticErrorModel : public ErrorModelBase
{
  protected:
    double packetErrorRate;
    double bitErrorRate;
    double symbolErrorRate;

  protected:
    virtual void initialize(int stage) override;

  public:
    StochasticErrorModel();

    virtual std::ostream& printToStream(std::ostream& stream, int level, int evFlags = 0) const override;

    virtual double computePacketErrorRate(const ISnir *snir, IRadioSignal::SignalPart part) const override;
    virtual double computeBitErrorRate(const ISnir *snir, IRadioSignal::SignalPart part) const override;
    virtual double computeSymbolErrorRate(const ISnir *snir, IRadioSignal::SignalPart part) const override;
};

} // namespace physicallayer

} // namespace inet

#endif

