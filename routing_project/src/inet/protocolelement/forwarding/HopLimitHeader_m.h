//
// Generated file, do not edit! Created by opp_msgtool 6.0 from inet/protocolelement/forwarding/HopLimitHeader.msg.
//

#ifndef __INET_HOPLIMITHEADER_M_H
#define __INET_HOPLIMITHEADER_M_H

#if defined(__clang__)
#  pragma clang diagnostic ignored "-Wreserved-id-macro"
#endif
#include <omnetpp.h>

// opp_msgtool version check
#define MSGC_VERSION 0x0600
#if (MSGC_VERSION!=OMNETPP_VERSION)
#    error Version mismatch! Probably this file was generated by an earlier version of opp_msgtool: 'make clean' should help.
#endif

// dll export symbol
#ifndef INET_API
#  if defined(INET_EXPORT)
#    define INET_API  OPP_DLLEXPORT
#  elif defined(INET_IMPORT)
#    define INET_API  OPP_DLLIMPORT
#  else
#    define INET_API
#  endif
#endif


namespace inet {

class HopLimitHeader;

}  // namespace inet

#include "inet/common/INETDefs_m.h" // import inet.common.INETDefs

#include "inet/common/packet/chunk/Chunk_m.h" // import inet.common.packet.chunk.Chunk


namespace inet {

/**
 * Class generated from <tt>inet/protocolelement/forwarding/HopLimitHeader.msg:13</tt> by opp_msgtool.
 * <pre>
 * class HopLimitHeader extends FieldsChunk
 * {
 *     chunkLength = B(2);
 *     int hopLimit;
 * }
 * </pre>
 */
class INET_API HopLimitHeader : public ::inet::FieldsChunk
{
  protected:
    int hopLimit = 0;

  private:
    void copy(const HopLimitHeader& other);

  protected:
    bool operator==(const HopLimitHeader&) = delete;

  public:
    HopLimitHeader();
    HopLimitHeader(const HopLimitHeader& other);
    virtual ~HopLimitHeader();
    HopLimitHeader& operator=(const HopLimitHeader& other);
    virtual HopLimitHeader *dup() const override {return new HopLimitHeader(*this);}
    virtual void parsimPack(omnetpp::cCommBuffer *b) const override;
    virtual void parsimUnpack(omnetpp::cCommBuffer *b) override;

    virtual int getHopLimit() const;
    virtual void setHopLimit(int hopLimit);
};

inline void doParsimPacking(omnetpp::cCommBuffer *b, const HopLimitHeader& obj) {obj.parsimPack(b);}
inline void doParsimUnpacking(omnetpp::cCommBuffer *b, HopLimitHeader& obj) {obj.parsimUnpack(b);}


}  // namespace inet


namespace omnetpp {

template<> inline inet::HopLimitHeader *fromAnyPtr(any_ptr ptr) { return check_and_cast<inet::HopLimitHeader*>(ptr.get<cObject>()); }

}  // namespace omnetpp

#endif // ifndef __INET_HOPLIMITHEADER_M_H

