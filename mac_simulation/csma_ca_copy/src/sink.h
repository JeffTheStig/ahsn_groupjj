/* Header sink
 *
 * Author: Leonardo Bonati
 * Created on Feb. 2018
 *
 */

#include <omnetpp.h>

using namespace omnetpp;

namespace csma_ca {

class SinkNodeCSMACA : public cSimpleModule
{
  private:
    int received_pkts;
    int collided;
    int net;
    simsignal_t sig_avg_delivery_ratio;
    simsignal_t sig_avg_latency;
//    simsignal_t sig_latency;
    simsignal_t sig_avg_energy_cons;
//    simsignal_t sig_energy_cons;
    simsignal_t sig_pkts_received;
    simsignal_t sig_collided;
//    simsignal_t sig_pkts_timeout;
    simsignal_t sig_pkts_dropped;
//    simsignal_t sig_retries;
    simsignal_t sig_avg_retries;
    simsignal_t sig_collided_net;
    simsignal_t sig_pkts_received_net;

  protected:
    virtual void initialize();
    virtual void handleMessage(cMessage *msg);
    virtual void finish();

  public:
    bool get_channel_state();
    void change_channel_state(bool state);
};

Define_Module(SinkNodeCSMACA);

}; // namespace
